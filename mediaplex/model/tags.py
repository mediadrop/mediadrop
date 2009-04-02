from datetime import datetime
from sqlalchemy import Table, ForeignKey, Column
from sqlalchemy.types import String, Unicode, UnicodeText, Integer, DateTime, Boolean, Float
from sqlalchemy.orm import mapper, relation, backref, synonym

from mediaplex.model import DeclarativeBase, metadata, DBSession


tags = Table('tags', metadata,
    Column('id', Integer, autoincrement=True, primary_key=True),
    Column('name', Unicode(50), unique=True, nullable=False),
    Column('slug', String(50), unique=True, nullable=False),
    mysql_engine='InnoDB',
    mysql_charset='utf8'
)


class Tag(object):
    """Tag definition"""

    def __repr__(self):
        return '<Tag: %s>' % self.name

    def __unicode__(self):
        return self.name


mapper(Tag, tags)
