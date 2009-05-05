"""
Comment Model

Other modules should create a join table with a UNIQUE constraint on the comment ID:
    blahs_comments = Table('blahs_comments', metadata,
        Column('blah_id', Integer, ForeignKey('blahs.id', onupdate='CASCADE', ondelete='CASCADE'),
            primary_key=True),
        Column('comment_id', Integer, ForeignKey('comments.id', onupdate='CASCADE', ondelete='CASCADE'),
            primary_key=True, unique=True))

A relation property should be defined to include the CommentTypeExtension.
Be sure to pass it the same value as the backref argument to enable reverse lookup.
Finally the argument single_parent=True should also be included.
    'comments': relation(Comment, secondary=media_comments, backref='media', single_parent=True,
        extension=CommentTypeExtension('media')),

"""
from datetime import datetime
from sqlalchemy import Table, ForeignKey, Column, sql
from sqlalchemy.types import String, Unicode, UnicodeText, Integer, DateTime, Boolean, Float
from sqlalchemy.orm import mapper, relation, backref, synonym, composite, column_property, validates, interfaces

from mediaplex.model import DeclarativeBase, metadata, DBSession, authors
from mediaplex.model.status import Status, StatusSet, StatusComparator, StatusType, StatusTypeExtension


TRASH = Status('trash', 1)
PUBLISH = Status('publish', 2)
PENDING_REVIEW = Status('pending_review', 4)
USER_FLAGGED = Status('user_flagged', 8)

STATUSES = dict((int(s), s) for s in (TRASH, PUBLISH, PENDING_REVIEW, USER_FLAGGED))
"""Dictionary of allowed statuses, bitmask value(int) => Status(unicode) instance"""

class CommentStatusSet(StatusSet):
    _valid_els = STATUSES


comments = Table('comments', metadata,
    Column('id', Integer, autoincrement=True, primary_key=True),
    Column('type', Unicode(15), nullable=False),
    Column('subject', Unicode(100)),
    Column('created_on', DateTime, default=datetime.now, nullable=False),
    Column('modified_on', DateTime, default=datetime.now, onupdate=datetime.now, nullable=False),
    Column('status', StatusType(CommentStatusSet), default=PUBLISH, nullable=False),
    Column('author_name', Unicode(50), nullable=False),
    Column('author_email', Unicode(255)),
    Column('author_ip', Integer),
    Column('body', UnicodeText, nullable=False),
    mysql_engine='InnoDB',
    mysql_charset='utf8'
)


class Comment(object):
    """Comment Model

    :param parent:
      The object this Comment belongs to, provided for convenience mostly.

    :param type:
      The relation to use when looking up the parent object of this Comment.

    :param author:
      An instance of mediaplex.model.author.Author.

    """
    def __repr__(self):
        return '<Comment: %d subject="%s">' % (self.id, self.subject)

    def __unicode__(self):
        return self.subject

    def _get_parent(self):
        return getattr(self, self.type, None)
    def _set_parent(self, parent):
        return setattr(self, self.type, parent)
    parent = property(_get_parent, _set_parent)


class CommentTypeExtension(interfaces.AttributeExtension):
    """Comment Type Attribute Handler

    Use this attribute extension when defining a relation() to Comment.
    It tells us which relation to use when looking for a Comment's parent object.

    :param type:
      The value to assign to Comment.type, should match the relation()'s backref.

    """
    def __init__(self, type):
        self.type = type

    def append(self, state, value, initiator):
        value.type = self.type
        return value

    def set(self, value, oldvalue, initiator):
        value.type = self.type
        return value


mapper(Comment, comments, properties={
    'status': column_property(comments.c.status, extension=StatusTypeExtension(), comparator_factory=StatusComparator),
    'author': composite(authors.AuthorWithIP,
        comments.c.author_name,
        comments.c.author_email,
        comments.c.author_ip),
})
