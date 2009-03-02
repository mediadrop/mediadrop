from datetime import datetime

from sqlalchemy import Table, ForeignKey, Column
from sqlalchemy.types import String, Unicode, UnicodeText, Integer, DateTime, Boolean, Float
from sqlalchemy.orm import mapper, relation, backref, synonym

from mediaplex.model import DeclarativeBase, metadata, DBSession
from mediaplex.model.comments import Comment
from mediaplex.model.tags import Tag


videos = Table('videos', metadata,
    Column('id', Integer, autoincrement=True, primary_key=True),
    Column('slug', String(50), unique=True, nullable=False),
    Column('title', Unicode(50), nullable=False),
    Column('url', String(255), nullable=False),
    Column('length', Integer, nullable=False),
    Column('date_added', DateTime, default=datetime.now, nullable=False),
    Column('date_modified', DateTime, default=datetime.now, onupdate=datetime.now, nullable=False),
    Column('views', Integer, default=0, nullable=False),
    Column('rating_sum', Integer, default=0, nullable=False),
    Column('rating_votes', Integer, default=0, nullable=False),
    Column('description', UnicodeText),
    mysql_engine='InnoDB',
    mysql_charset='utf8'
)

videos_comments = Table('videos_comments', metadata,
    Column('video_id', Integer, ForeignKey('videos.id', onupdate='CASCADE', ondelete='CASCADE'),
        primary_key=True),
    Column('comment_id', Integer, ForeignKey('comments.id', onupdate='CASCADE', ondelete='CASCADE'),
        primary_key=True, unique=True)
)

videos_tags = Table('videos_tags', metadata,
    Column('video_id', Integer, ForeignKey('videos.id', onupdate='CASCADE', ondelete='CASCADE'),
        primary_key=True),
    Column('tag_id', Integer, ForeignKey('tags.id', onupdate='CASCADE', ondelete='CASCADE'),
        primary_key=True)
)


class Video(object):
    """Video definition"""

    def __repr__(self):
        return '<Video: title=%s>' % self.title

    def __unicode__(self):
        return self.title

    def add_rating(self, rating):
        self.rating_sum += rating
        self.rating_votes += 1
        return self


mapper(Video, videos, properties={
    'comments': relation(Comment, secondary=videos_comments, backref='parent'),
    'tags': relation(Tag, secondary=videos_tags, backref='videos')
})
