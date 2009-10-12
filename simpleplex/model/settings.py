from sqlalchemy import Table, ForeignKey, Column
from sqlalchemy.types import String, Unicode, UnicodeText, Integer, Boolean, Float
from sqlalchemy.orm import mapper, relation, backref, synonym, interfaces, validates

from simpleplex.model import DeclarativeBase, metadata, DBSession, slugify, _mtm_count_property


settings = Table('settings', metadata,
    Column('id', Integer, autoincrement=True, primary_key=True),
    Column('key', Unicode(255), nullable=False),
    Column('value', UnicodeText),
    mysql_engine='InnoDB',
    mysql_charset='utf8'
)


class Setting(object):
    """Setting definition
    """
    def __init__(self, key=None, value=None):
        self.key = key or None
        self.value = value or None

    def __repr__(self):
        return '<Setting: %s = %s>' % (self.key, self.value)

    def __unicode__(self):
        return '%s = %s' % (self.key, self.value)

mapper(Setting, settings)
