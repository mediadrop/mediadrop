"""
Custom Status Datatype for SQLAlchemy ORM

A special extension of the ``set`` collection which allows only predetermined
values to be used. Values are given bitmask values which can be saved to either
an INT or MySQL SET database column. This gives us a convenient API to work
with on the application-level whether we have MySQL under the hood or not.

Defining the allowed statuses::

    >>> class MediaStatus(Status):
    ...    values = ('trash', 'publish', 'draft', 'unencoded', 'unreviewed')

.. warning::

    If you are using a MySQL SET column type in the DB, the values must be
    defined in the *same order* in both places.

Defining the status column on the Table::

    Table('media',
        # ...
        Column('status', StatusType(MediaStatus), default=MediaStatus('publish'), nullable=False),
        # ...
    )

Setting up SQLALchemy mapper with the custom attribute behaviour::

    mapper(Media, media, properties={
        'status': status_column_property(media.c.status),
    })

Querying by status follows the API of ``set`` as closely as possible::

    >>> # Grab rows with *exaclty* this status:
    >>> DBSession.query(Media).filter(Media.status == 'draft,unencoded,unreviewed')
    >>> DBSession.query(Media).filter(Media.status == ['draft','unencoded','unreviewed'])
    >>> DBSession.query(Media).filter(Media.status == MediaStatus(['draft','unencoded','unreviewed'])
    >>> DBSession.query(Media).filter(Media.status == 28)

    >>> # Grab rows with *at least* all of these statuses:
    >>> DBSession.query(Media).filter(Media.status.issuperset('draft,unencoded'))
    >>> DBSession.query(Media).filter(Media.status >= 'draft,unencoded')

    >>> # Grab rows with *at least* any one of these statuses:
    >>> DBSession.query(Media).filter(Media.status.intersects('unreviewed,unencoded'))

    >>> # Grab rows with one or more of these statuses but no others:
    >>> DBSession.query(Media).filter(Media.status.issuperset('draft,unencoded'))
    >>> DBSession.query(Media).filter(Media.status >= 'draft,unencoded')

    >>> # Grab rows which don't contain any of the given statuses:
    >>> DBSession.query(Media).filter(Media.status.excludes('trash'))

Working with statuses once you've got a row::

    >>> media_inst.status = 'unreviewed,draft'
    >>> media_inst.status
    unreviewed,draft
    >>> int(media_inst.status)
    16

    >>> media_inst.status.add('unencoded')
    >>> media_inst.status
    unreviewed,draft,unencoded

    >>> 'unreviewed' in media_inst.status
    True

All of the following raise a ``ValueError`` because ``randomchance`` is not
in :attr:`MediaStatus.map`::

    'randomchance' in media_inst.status

    DBSession.query(Media).filter(Media.status.excludes('randomchance'))

    some_status = MediaStatus()
    some_status.add('randomchance')


An overview of the components that make this happen:

* :class:`Status` is the collection used to represent the column's bitmask values
  and their on-off state. Its supports integer and string IO.

* :class:`StatusBit` is an individual value that can be stored in the column's bitmask.
  It is a unicode string with a bit representation for the bitmask column,
  available by casting to int.

* :class:`StatusType` is an extended Integer column which automatically converts
  integer values from the database to :class:`Status` instances and :class:`Status`
  instances back to integer values for saving.

* :class:`StatusTypeExtension` simply ensures that any value set to media_inst.status
  is *always* an instance of the appropriate Status subclass.

* :class:`StatusComparator` overloads the default query behaviour of the status column.
  It handles the basic bit-wise operators for you, but for now, more complex
  operations will have to be done by hand.

* :func:`status_column_property` helps create the SQLAlchemy mapper column
  property with the necessary arguments.

"""

from sqlalchemy import sql, types
from sqlalchemy.orm import interfaces, properties, column_property


class StatusBit(object):
    """
    Status string which can be converted to int and mashed into a bitmask::

        >>> s = StatusBit('trash', 1)
        >>> s
        trash
        >>> int(s)
        1

    """
    def __init__(self, unival, intval):
        self._unival = unicode(unival)
        self._intval = int(intval)

    def __repr__(self):
        return self._unival

    def __str__(self):
        return self._unival.encode('utf8')

    def __unicode__(self):
        return self._unival

    def __int__(self):
        return int(self._intval)

    def __eq__(self, other):
        if isinstance(other, (StatusBit, int, long)):
            return int(self) == int(other)
        else:
            return unicode(self) == unicode(other)


class Status(set):
    """
    Orderless Collection of StatusBits

    All operations which involve adding/removing specific elements validate
    their arguments against the :attr:`map`. If you try to even discard
    an invalid status, an exception is thrown. This helps prevent developer error
    and provides constant-like behaviour for basic strings without the need for
    actual constants (which are awkward to work with inside Genshi templates).

    Operations which work with other sets, such as object construction, unions,
    upates, etc can accept any collection (so long as it contains no invalid
    elements) as well as any valid bitmask or string with comma separated elements.

    Basic Usage::

        >>> map = map_values_to_bits(['trash', 'publish', 'draft', 'unencoded', 'unreviewed'])
        >>> s1 = Status(['draft', 'unreviewed'], map=map)
        >>> int(s) == 4 + 16
        True

    It is recommended that Status be extended to simplify usage::

        >>> class MediaStatus(Status):
        ...    values = ('trash', 'publish', 'draft', 'unencoded', 'unreviewed')
        ...
        >>> s2 = MediaStatus('draft,unreviewed')
        >>> int(s2) == int(s1)
        True

        >>> s3 = MediaStatus(4 + 16)
        >>> s3 == s2
        True

        >>> s3
        draft,unreviewed

        >>> int(s3)
        20

    .. warning::

        If you are using a MySQL SET column type in the DB, the values must be
        defined in the *same order* in both places.

    .. attribute:: map

        A dict of :class:`StatusBit` instances keyed by their int bit values.

    .. attribute:: values

        An iterable to generate the map from. Provided for convenience, simply
        sets the map with the result of :func:`map_values_to_bits`.

    """
    values = None
    map = None

    def __new__(cls, *args, **kwargs):
        if cls.map is None and cls.values:
            cls.map = map_values_to_bits(cls.values)
        elif 'map' in kwargs:
            cls.map = map_values_to_bits(kwargs.pop('map'))
        return set.__new__(cls, *args, **kwargs)

    def __init__(self, seq=None):
        if seq:
            seq = self._validate_seq(seq)
        else:
            seq = []
        return super(Status, self).__init__(seq)

    def __int__(self):
        return sum(int(s) for s in self)

    def __unicode__(self):
        return ','.join(self)

    def _validate_el(self, status):
        """Parse the status argument into a single StatusBit instance.

        The arg may be int, string, or a StatusBit instance, but if it is not found in
        the :attr:`map`, a ValueError is thrown.
        """
        try:
            if isinstance(status, (StatusBit, int, long)):
                return self.map[int(status)]
            for i, s in self.map.items():
                if s == unicode(status):
                    return self.map[i]
        except (KeyError, ValueError):
            pass
        raise ValueError, 'Invalid status element "%s"' % status

    def _validate_seq(self, seq):
        """Parse the sequence argument into a collection of StatusBit instances.

        The arg may be int, string, StatusBit, or any collection-like object, but if
        any elements fail validation (are not found in the :attr:`map`) then
        a ValueError is raised.
        """
        if isinstance(seq, (int, long)):
            bitmask = seq
            seq = [s for s in self.map.itervalues() if bitmask & s._intval == s._intval]
            if bitmask > sum(s._intval for s in seq):
                raise ValueError, 'Invalid status sequence bitmask %s - picked out %s' % (bitmask, seq)
        elif isinstance(seq, basestring):
            seq = [self._validate_el(s) for s in unicode(seq).split(',')]
        elif isinstance(seq, StatusBit):
            seq = (StatusBit,)
        elif isinstance(seq, Status):
            pass
        elif isinstance(seq, (list, tuple)):
            seq = [self._validate_el(s) for s in seq]
        else:
            raise ValueError, 'Invalid status sequence "%s"' % seq
        return seq

    def __contains__(self, el):
        return super(Status, self).__contains__(self._validate_el(el))
    def add(self, el):
        return super(Status, self).add(self._validate_el(el))
    def remove(self, el):
        return super(Status, self).remove(self._validate_el(el))
    def discard(self, el):
        return super(Status, self).discard(self._validate_el(el))
    def difference(self, seq):
        return super(Status, self).difference(self._validate_seq(seq))
    def difference_update(self, seq):
        return super(Status, self).difference_update(self._validate_seq(seq))
    def intersection(self, seq):
        return super(Status, self).intersection(self._validate_seq(seq))
    def intersection_update(self, seq):
        return super(Status, self).intersection_update(self._validate_seq(seq))
    def symetric_difference(self, seq):
        return super(Status, self).symetric_difference(self._validate_seq(seq))
    def symetric_difference_update(self, seq):
        return super(Status, self).symetric_difference_update(self._validate_seq(seq))
    def union(self, seq):
        return super(Status, self).union(self._validate_seq(seq))
    def update(self, seq):
        return super(Status, self).update(self._validate_seq(seq))


class StatusType(types.MutableType, types.TypeDecorator):
    """
    Custom Column Type

    Converts of the status bitmask from the database level into a Status
    and back again when saving.

    Due to the nature of the Status class, this will work seamlessly with
    with SET or INT database columns.

    """
    impl = types.Integer

    def __init__(self, status_set_class):
        """
        :param status_set_class:
          The collection class to convert the bitmask values to. Should inherit Status.
        """
        self.status_set_class = status_set_class
        super(StatusType, self).__init__()

    def process_bind_param(self, value, dialect):
        return int(value)

    def process_result_value(self, value, dialect):
        return self.status_set_class(value)

    def copy_value(self, value):
        if value is None:
            return None
        return value.copy()


class StatusTypeExtension(interfaces.AttributeExtension):
    """Status Type ORM Extension

    Provides intelligent type handling, converting raw values into the proper collection::

        >>> obj.status = 'draft'
        >>> obj.status = 8
        >>> isinstance(obj.status, Status)
        True
        >>> obj.status
        draft

    """
    def set(self, state, value, oldvalue, initiator):
        status_set_class = initiator.parent_token.columns[0].type.status_set_class
        if value is not None and not isinstance(value, status_set_class):
            value = status_set_class(value)
        return super(StatusTypeExtension, self).set(state, value, oldvalue, initiator)


class StatusComparator(properties.ColumnProperty.Comparator):
    """
    Status Column Comparator for Querying the DB
    """
    def __eq__(self, other):
        other = self._status_set_class(other)
        return self._column.op('=')(int(other))

    def intersects(self, criterion=None):
        """Match statuses that have at least one of the elements in the given set."""
        criterion = int(self._status_set_class(criterion))
        return self._column.op('&')(criterion)

    def excludes(self, criterion=None):
        """Match statuses that don't have any of the elements in the given set."""
        return sql.not_(self.intersects(criterion))

    def issuperset(self, criterion=None):
        """Match statuses that contain all elements of the given set while allowing others."""
        criterion = int(self._status_set_class(criterion))
        return self._column.op('&')(criterion) == criterion
    __ge__ = issuperset

    def issubset(self, criterion=None):
        """Match statuses that contain some elements of the given set while disallowing all others."""
        criterion = int(self._status_set_class(criterion))
        return sql.and_(self._column.op('&')(criterion),
                        self._column.op('& ~')(criterion) == 0)
    __le__ = issubset

    @property
    def _column(self):
        return self.__clause_element__()

    @property
    def _status_set_class(self):
        return self._column.type.status_set_class


def map_values_to_bits(values):
    """Create the necessary :class:`StatusBit` instances for the given values::

        >>> map = map_values_to_bits(['trash', 'publish', 'draft', 'unencoded', 'unreviewed'])
        >>> map
        {1: trash, 2: publish, 4: draft, 8: unencoded, 16: unreviewed}
        >>> map[1] is StatusBit
        True

    .. warning::

        If you are using a MySQL SET column in your database, the values
        given here must match the order they are defined in the database.
        If not, the wrong values will be get and set.

    :param values: string values
    :type values: iterable
    :return: New :class:`StatusBit` instances keyed by their integer bit values
    :rtype: dict

    """
    map = {}
    for i, strval in enumerate(values):
        bitval = 1 << i
        map[bitval] = StatusBit(strval, bitval)
    return map


def status_column_property(column, **kwargs):
    """Return a column property to feed the :func:`sqlalchemy.orm.mapper`.

    Provided for convience, this simply creates a column property with the
    necessary :class:`StatusTypeExtension` and :class:`StatusComparator`,
    in addition to whatever other column property arguments you provide.

    :param column: The status column on your table
    :type column: :class:`sqlalchemy.Column` with type :class:`StatusType`
    :param kwargs: Passed to :func:`sqlalchemy.orm.column_property`
    :rtype: A configured :class:`sqlalchemy.orm.properties.ColumnProperty`

    """
    extension = kwargs.pop('extension', [])
    extension.append(StatusTypeExtension())
    comparator_factory = kwargs.pop('comparator_factory', StatusComparator)
    return column_property(
        column,
        extension=extension,
        comparator_factory=comparator_factory,
        **kwargs
    )


def status_where(column, include=None, exclude=None):
    """Generate a bitwise WHERE clause to include and/or exclude statuses.

    :param column: A :class:`sqlalchemy.Column` instance with type :class:`StatusType`.
    :param include: Statuses that must be included to match.
    :param exclude: Statuses that must not be included to match.

    """
    status_set = column.type.status_set_class
    clauses = dict(include=include, exclude=exclude)
    where = []
    for op, value in clauses.iteritems():
        intval = int(status_set(value))
        where.append(column.op('&')(intval) == (op == 'include' and intval or sql.text('0')))
    return where
