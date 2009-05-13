"""
SQLAlchemy (DB-agnostic) implementation MySQL's SET Datatype

An column abstraction which allows us to store any combination of predefined values
within a single database field. This implementation is that the code works whether
the database is using a MySQL SET column or a plain old Integer, so portability is
maintained.

Setting up our SQLAlchemy model:

    # First we must define the allowed statuses, and their value for the column:
    TRASH    = Status('trash',   1)
    PUBLISH  = Status('publish', 2)
    DRAFT    = Status('draft',   4)

    STATUSES = dict((int(s), s) for s in (TRASH, PUBLISH, DRAFT))

    # Then subclass StatusSet to define valid elements
    class VideoStatusSet(StatusSet):
        _valid_els = STATUSES

    # Defining the status column on the Table:
    Table('media',
        # ...
        Column('status', StatusType(VideoStatusSet), default=PUBLISH, nullable=False),
        # ...
    )

    # And setting up SQLALchemy mapper with the custom attribute behaviour:
    mapper(Media, media, properties={
        'status': column_property(media.c.status, extension=StatusTypeExtension(), comparator_factory=StatusComparator),
    })

Querying for rows based on their status:

    # These are all equivalent inputs:
    # Grabs rows with exactly this status:
    DBSession.query(Media).filter(Media.status == 'draft,pending_encoding,pending_review')
    DBSession.query(Media).filter(Media.status == ['draft','pending_encoding','pending_review'])
    DBSession.query(Media).filter(Media.status == VideoStatusSet(['draft','pending_encoding','pending_review'])
    DBSession.query(Media).filter(Media.status == 28)

    # Grab rows with *at least* all of these statuses:
    DBSession.query(Media).filter(Media.status.contains_all('draft,pending_encoding')

    # Grab rows with *at least* either of these statuses:
    DBSession.query(Media).filter(Media.status.contains_some('pending_review,pending_encoding')

    # Grab rows which don't contain any of the given statuses:
    DBSession.query(Media).filter(Media.status.contains_none('trash')

Working with statuses once you've got a row:

    media_inst.status = 'trash'
    media_inst.status.discard('trash')
    media_inst.status.add('publish')
    media_inst.status = [DRAFT, PENDING_REVIEW]
    media_inst.status = 8
    is_pending_review = 'pending_review' in media_inst.status

If at any time you try to do something with an invalid status, a ValueError is thrown:

    fail = 'randomchance' in media_inst.status
    DBSession.query(Media).filter(Media.status.contains_none('randomchance'))
    some_status = VideoStatusSet
    some_status.add('randomchance')


An overview of the components that make this happen:

``StatusType`` is a decorated Integer column. It gives us StatusSet instances
to work with and automatically converts the StatusSet back into an Integer
when saving.

``StatusSet`` is the collection used to represent the column's bitmask values.
Subclass it with a _valid_els property, a dictionary of valid statuses for the
column in question. If we typo or otherwise attempt an operation with
a nonexistant value, a ValueError is thrown.

``Status`` is an individual value that can be stored in the column's bitmask.
It is a unicode string with a bit representation for the bitmask column,
available by casting to int.

``StatusComparator`` overloads the default query behaviour of the status column.
It handles the basic bit-wise operators for you, but for now, more complex
operations will have to be done by hand.

``StatusTypeExtension`` simply ensures that any value set to media_inst.status
is *always* an instance of the appropriate StatusSet subclass.

"""

from sqlalchemy import sql, types
from sqlalchemy.orm import interfaces, properties


class Status(object):
    """Status string which can be converted to int and mashed into a bitmask"""
    def __init__(self, unival, intval, *args, **kwargs):
        self._unival = unicode(unival)
        self._intval = int(intval)

    def __str__(self):
        return self._unival.encode('utf8')

    def __repr__(self):
        return self._unival

    def __unicode__(self):
        return self._unival

    def __int__(self):
        return int(self._intval)

    def __eq__(self, other):
        if isinstance(other, (Status, int, long)):
            return int(self) == int(other)
        else:
            return unicode(self) == unicode(other)


class StatusSet(set):
    """Orderless Collection of Statuses

    All operations which involve adding/removing specific elements validate
    their arguments against the _valid_els property. If you try to even discard
    an invalid status, an exception is thrown. This helps prevent developer error
    and provides constant-like behaviour for basic strings without the need for
    actual constants (which are awkward to work with inside Genshi templates).

    Operations which work with other sets, such as object construction, unions,
    upates, etc can accept any collection (so long as it contains no invalid
    elements) as well as any valid bitmask or string with comma separated elements.

    Examples of acceptable sequence input:
        s = StatusSet(['draft', 'pending_review'])
        s = StatusSet('draft,pending_review')
        s = StatusSet(11)       # the equivalent of a 1101 bitmask
        print int(s) # prints 11, the equivalent of a 1101 bitmask

    Note that this class should typically be subclassed to override _valid_els.

    """
    _valid_els = {}

    def __init__(self, seq=None):
        if seq:
            return super(StatusSet, self).__init__(self._validate_seq(seq))

    def __int__(self):
        return sum(int(s) for s in self)

    def __unicode__(self):
        return ','.join(self)

    def _validate_el(self, status):
        """Parse the status argument into a single Status instance.

        The arg may be int, string, or a Status instance, but if it is not found in
        the _valid_els property, a ValueError is thrown.
        """
        try:
            if isinstance(status, (Status, int, long)):
                return self._valid_els[int(status)]
            for i, s in self._valid_els.items():
                if s == unicode(status):
                    return self._valid_els[i]
        except (KeyError, ValueError):
            pass
        raise ValueError, 'Invalid status element "%s"' % status

    def _validate_seq(self, seq):
        """Parse the sequence argument into a collection of Status instances.

        The arg may be int, string, Status, or any collection-like object, but if
        any elements fail validation (are not found in the _valid_els property) then
        the whole operation aborts with a ValueError.
        """
        if isinstance(seq, (int, long)):
            bitmask = seq
            seq = [s for s in self._valid_els.itervalues() if bitmask & s._intval == s._intval]
            if bitmask > sum(s._intval for s in seq):
                raise ValueError, 'Invalid status sequence bitmask %s - picked out %s' % (bitmask, seq)
        elif isinstance(seq, basestring):
            seq = [self._validate_el(s) for s in unicode(seq).split(',')]
        elif isinstance(seq, Status):
            seq = (Status,)
        elif isinstance(seq, StatusSet):
            pass
        elif isinstance(seq, (list, tuple)):
            seq = [self._validate_el(s) for s in seq]
        else:
            raise ValueError, 'Invalid status sequence "%s"' % seq
        return seq

    def __contains__(self, el):
        return super(StatusSet, self).__contains__(self._validate_el(el))
    def add(self, el):
        return super(StatusSet, self).add(self._validate_el(el))
    def remove(self, el):
        return super(StatusSet, self).remove(self._validate_el(el))
    def discard(self, el):
        return super(StatusSet, self).discard(self._validate_el(el))
    def difference(self, seq):
        return super(StatusSet, self).difference(self._validate_seq(seq))
    def difference_update(self, seq):
        return super(StatusSet, self).difference_update(self._validate_seq(seq))
    def intersection(self, seq):
        return super(StatusSet, self).intersection(self._validate_seq(seq))
    def intersection_update(self, seq):
        return super(StatusSet, self).intersection_update(self._validate_seq(seq))
    def symetric_difference(self, seq):
        return super(StatusSet, self).symetric_difference(self._validate_seq(seq))
    def symetric_difference_update(self, seq):
        return super(StatusSet, self).symetric_difference_update(self._validate_seq(seq))
    def union(self, seq):
        return super(StatusSet, self).union(self._validate_seq(seq))
    def update(self, seq):
        return super(StatusSet, self).update(self._validate_seq(seq))


class StatusType(types.MutableType, types.TypeDecorator):
    """Custom Column Type

    Converts of the status bitmask from the database level into a StatusSet
    and back again when saving.

    Due to the nature of the StatusSet class, this will work seamlessly with
    with SET or INT database columns.

    :param status_set_class:
      The collection class to convert the bitmask values to. Should inherit StatusSet.

    """
    impl = types.Integer

    def __init__(self, status_set_class):
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

    Provides intelligent type handling, converting raw values into the proper collection.
        > obj.status = 'draft'
        > obj.status = 8
        > print obj.status
        <StatusType.status_set_class>
    """
    def set(self, state, value, oldvalue, initiator):
        status_set_class = initiator.parent_token.columns[0].type.status_set_class
        if value is not None and not isinstance(value, status_set_class):
            value = status_set_class(value)
        return super(StatusTypeExtension, self).set(state, value, oldvalue, initiator)


class StatusComparator(properties.ColumnProperty.Comparator):
    """Status Column Comparator for Querying the DB"""
    def __eq__(self, other):
        other = self._status_set_class(other)
        return self._column.op('=')(int(other))

    def intersects(self, criterion=None):
        """Match statuses that have at least one of the elements in the given set"""
        criterion = int(self._status_set_class(criterion))
        return self._column.op('&')(criterion)

    def excludes(self, criterion=None):
        """Match statuses that don't have any of the elements in the given set"""
        return sql.not_(self.intersects(criterion))

    def issuperset(self, criterion=None):
        """Match statuses that contain all elements of the given set while allowing others"""
        criterion = int(self._status_set_class(criterion))
        return self._column.op('&')(criterion) == criterion
    __ge__ = issuperset

    def issubset(self, criterion=None):
        """Match statuses that contain some elements of the given set while disallowing all others"""
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
