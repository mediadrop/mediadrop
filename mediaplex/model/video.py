from datetime import datetime

from sqlalchemy import Table, ForeignKey, Column
from sqlalchemy.types import String, Unicode, UnicodeText, Integer, DateTime, Boolean, Float
from sqlalchemy.orm import relation, backref, synonym

from mediaplex.model import DeclarativeBase, metadata, DBSession


class Video(DeclarativeBase):
    """Video definition"""
    __tablename__ = 'videos'

    id = Column(Integer, autoincrement=True, primary_key=True)
    slug = Column(String(50), unique=True, nullable=False)
    title = Column(Unicode(50), nullable=False)
    url = Column(String(255), nullable=False)
    length = Column(Integer, nullable=False)
    date_added = Column(DateTime, default=datetime.now, nullable=False)
    date_modified = Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)
    views = Column(Integer, default=0, nullable=False)
    description = Column(UnicodeText)

    def __repr__(self):
        return '<Video: title=%s>' % self.title

    def __unicode__(self):
        return self.title
