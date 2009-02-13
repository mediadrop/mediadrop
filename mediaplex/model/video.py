from datetime import datetime

from sqlalchemy import Table, ForeignKey, Column
from sqlalchemy.types import String, Unicode, UnicodeText, Integer, DateTime, Boolean, Float
from sqlalchemy.orm import mapper, relation, backref, synonym

from mediaplex.model import DeclarativeBase, metadata, DBSession


videos = Table('videos', metadata,
    Column('id', Integer, autoincrement=True, primary_key=True),
    Column('slug', String(50), unique=True, nullable=False),
    Column('title', Unicode(50), nullable=False),
    Column('url', String(255), nullable=False),
    Column('length', Integer, nullable=False),
    Column('date_added', DateTime, default=datetime.now, nullable=False),
    Column('date_modified', DateTime, default=datetime.now, onupdate=datetime.now, nullable=False),
    Column('views', Integer, default=0, nullable=False),
    Column('description', UnicodeText),
    mysql_engine='InnoDB',
    mysql_charset='utf8'
)

class Video(object):
    """Video definition"""

    def __repr__(self):
        return '<Video: title=%s>' % self.title

    def __unicode__(self):
        return self.title

mapper(Video, videos)
