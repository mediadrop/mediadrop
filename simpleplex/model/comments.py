"""
Comment Model

Other modules should create a join table with a UNIQUE constraint on the comment ID::

    medias_comments = Table('medias_comments', metadata,
        Column('media_id', Integer, ForeignKey('medias.id', onupdate='CASCADE', ondelete='CASCADE'),
            primary_key=True),
        Column('comment_id', Integer, ForeignKey('comments.id', onupdate='CASCADE', ondelete='CASCADE'),
            primary_key=True, unique=True))

A relation property should be defined to include the CommentTypeExtension.
Be sure to pass it the same value as the backref argument to enable reverse lookup.
Finally the argument single_parent=True should also be included. ::

    mapper(Media, medias, properties={
        'comments': relation(Comment, secondary=medias_comments,
            backref=backref('media', uselist=False), single_parent=True,
            extension=CommentTypeExtension('media')),
    })

Also include this property if you want to grab the comment count quickly::

    mapper(Media, medias, properties={
        'comment_count': comment_count_property(media_comments, 'comment_count'),
    })

.. note:: This uses a correlated subquery and can be executed when you first call
          ``media_item.comment_count`` or during the initial query by including
          the following option::

              DBSession.query(Media).options(undefer('comment_count')).all()

"""
from datetime import datetime
from sqlalchemy import Table, ForeignKey, Column, sql
from sqlalchemy.types import String, Unicode, UnicodeText, Integer, DateTime, Boolean, Float
from sqlalchemy.orm import mapper, relation, backref, synonym, composite, column_property, validates, interfaces

from simpleplex.model import DeclarativeBase, metadata, DBSession, AuthorWithIP, _mtm_count_property
from simpleplex.model.status import Status, StatusType, status_column_property


class CommentStatus(Status):
    values = ('trash', 'publish', 'unreviewed', 'user_flagged')


comments = Table('comments', metadata,
    Column('id', Integer, autoincrement=True, primary_key=True),
    Column('type', Unicode(15), nullable=False),
    Column('subject', Unicode(100)),
    Column('created_on', DateTime, default=datetime.now, nullable=False),
    Column('modified_on', DateTime, default=datetime.now, onupdate=datetime.now, nullable=False),
    Column('status', StatusType(CommentStatus), default=CommentStatus('publish'), nullable=False),
    Column('author_name', Unicode(50), nullable=False),
    Column('author_email', Unicode(255)),
    Column('author_ip', Integer, nullable=False),
    Column('body', UnicodeText, nullable=False),
    mysql_engine='InnoDB',
    mysql_charset='utf8'
)


class Comment(object):
    """Comment Model

    .. attribute:: type

        The relation name to use when looking up the parent object of this Comment.
        This is the name of the backref property which can be used to find the
        object that this Comment belongs to. Our convention is to have a controller
        by this name, with a 'view' action which accepts a slug, so we can
        auto-generate links to any comment's parent.

    .. attribute:: author

        An instance of :class:`simpleplex.model.author.AuthorWithIP`.

    """
    def __repr__(self):
        return '<Comment: %s subject="%s">' % (self.id, self.subject)

    def __unicode__(self):
        return self.subject

    def _get_parent(self):
        return getattr(self, self.type, None)
    def _set_parent(self, parent):
        return setattr(self, self.type, parent)
    parent = property(_get_parent, _set_parent, None, """
        The object this Comment belongs to, provided for convenience mostly.
        If the parent has not been eagerloaded, a query is executed automatically.
    """)


class CommentTypeExtension(interfaces.AttributeExtension):
    """
    Comment Type Auto-Mapping Extension

    When another module/class defines a :func:`sqlalchemy.orm.relation` to
    :class:`Comment` this extension should be included. This will automatically
    define the correct :attr:`Comment.type` when a comment is added to the
    related objects list of comments. This, in turn, allows us to look up the
    related object again from the comment alone, via :attr:`Comment.parent`.

    This is intended to make dealing with comments more convenient::

        >>> c = Comment()
        >>> print c.type
        None

        >>> m = Media()
        >>> m.comments.append(c)
        >>> print c.type
        'media'

    .. attribute:: type

        The value to assign to :attr:`Comment.type` when a comment is added to
        the related objects collection of comments.

    .. warning::

        The type given here and the name of the backref passed to
        :func:`sqlalchemy.orm.relation` must match for the reverse-lookup
        to work.

    """
    def __init__(self, type):
        self.type = type

    def append(self, state, value, initiator):
        value.type = self.type
        return value

    def set(self, value, oldvalue, initiator):
        # Pretty certain this should never be called on a relation property.
        raise NotImplemented


comment_count_property = _mtm_count_property


mapper(Comment, comments, properties={
    'status': status_column_property(comments.c.status),
    'author': composite(AuthorWithIP,
        comments.c.author_name,
        comments.c.author_email,
        comments.c.author_ip),
})
