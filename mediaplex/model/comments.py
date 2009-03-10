from datetime import datetime

from sqlalchemy import Table, ForeignKey, Column
from sqlalchemy.types import String, Unicode, UnicodeText, Integer, DateTime, Boolean, Float
from sqlalchemy.orm import mapper, relation, backref, synonym

from mediaplex.model import DeclarativeBase, metadata, DBSession


comments = Table('comments', metadata,
    Column('id', Integer, autoincrement=True, primary_key=True),
    Column('name', String(50), nullable=False),
    Column('subject', Unicode(50)),
    Column('date_added', DateTime, default=datetime.now, nullable=False),
    Column('date_modified', DateTime, default=datetime.now, onupdate=datetime.now, nullable=False),
    Column('body', UnicodeText, nullable=False),
    Column('reviewed', Boolean, default=False, nullable=False),
    mysql_engine='InnoDB',
    mysql_charset='utf8'
)

class Comment(object):
    """Comment definition"""

    def __repr__(self):
        return '<Comment: name="%s" subject="%s">' % (self.name, self.subject)

    def __unicode__(self):
        return self.subject

mapper(Comment, comments)
