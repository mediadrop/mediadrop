from datetime import datetime
from sqlalchemy import Table, ForeignKey, Column
from sqlalchemy.types import String, Unicode, UnicodeText, Integer, DateTime, Boolean, Float
from sqlalchemy.orm import mapper, relation, backref, synonym, composite
from sqlalchemy.orm.interfaces import AttributeExtension

from mediaplex.model import DeclarativeBase, metadata, DBSession
from mediaplex.model.author import Author


comments = Table('comments', metadata,
    Column('id', Integer, autoincrement=True, primary_key=True),
    Column('type', Unicode(15), nullable=False),
    Column('subject', Unicode(100)),
    Column('created_on', DateTime, default=datetime.now, nullable=False),
    Column('modified_on', DateTime, default=datetime.now, onupdate=datetime.now, nullable=False),
    Column('status', Unicode(15), default='unreviewed', nullable=False),
    Column('author_name', Unicode(50), nullable=False),
    Column('author_email', Unicode(255)),
    Column('body', UnicodeText, nullable=False),
    mysql_engine='InnoDB',
    mysql_charset='utf8'
)


class Comment(object):
    """Comment definition"""

    def __repr__(self):
        return '<Comment: %d subject="%s">' % (self.id, self.subject)

    def __unicode__(self):
        return self.subject


class CommentTypeExtension(AttributeExtension):
    """
    Automatically sets the Comment.type when it is
    added to a collection of comments belonging to a related object.
    """
    def __init__(self, type):
        self.type = type

    def append(self, state, value, initiator):
        value.type = self.type
        return value


mapper(Comment, comments, properties={
    'author': composite(Author, comments.c.author_name, comments.c.author_email)
})



#from mediaplex.model.video import MediaCommentExtension, Media
#media_comment_mapper = mapper(Comment, inherits=comment_mapper, polymorphic_identity='media', properties={
#    'parent': relation(Media, secondary=media_comments, backref='comments',
#        extension=MediaCommentExtension())
#})
