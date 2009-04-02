from datetime import datetime
from sqlalchemy import Table, ForeignKey, Column
from sqlalchemy.types import String, Unicode, UnicodeText, Integer, DateTime, Boolean, Float
from sqlalchemy.orm import mapper, relation, backref, synonym, composite

from mediaplex.model import DeclarativeBase, metadata, DBSession
from mediaplex.model.author import Author
from mediaplex.model.rating import Rating
from mediaplex.model.comments import Comment, CommentTypeExtension
from mediaplex.model.tags import Tag


test = Table('test', metadata,
    Column('id', Integer, autoincrement=True, primary_key=True),
    Column('data', Unicode(10), nullable=False),
)

test_comments = Table('test_comments', metadata,
    Column('test_id', Integer, ForeignKey('test.id', onupdate='CASCADE', ondelete='CASCADE'),
        primary_key=True),
    Column('comment_id', Integer, ForeignKey('comments.id', onupdate='CASCADE', ondelete='CASCADE'),
        primary_key=True, unique=True)
)

class Test(object):
    def __repr__(self):
        return '<Test: %s>' % self.data

mapper(Test, test, properties={
    'comments': relation(Comment, secondary=test_comments, backref='test', single_parent=True,
        extension=CommentTypeExtension('test')),
#    'comment_count': column_property(select().label('comment_count'))
})
