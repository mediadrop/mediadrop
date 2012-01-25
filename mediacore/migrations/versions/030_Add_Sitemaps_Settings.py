# This file is a part of MediaCore CE, Copyright 2009-2012 MediaCore Inc.
# The source code contained in this file is licensed under the GPL.
# See LICENSE.txt in the main project directory, for more information.

from sqlalchemy import *
from migrate import *

SETTINGS = [
    (u'sitemaps_display', u'enabled'),
]

metadata = MetaData()
settings = Table('settings', metadata,
    Column('id', Integer, autoincrement=True, primary_key=True),
    Column('key', Unicode(255), nullable=False, unique=True),
    Column('value', UnicodeText),
    mysql_engine='InnoDB',
    mysql_charset='utf8',
)

def upgrade(migrate_engine):
    metadata.bind = migrate_engine
    for key, value in SETTINGS:
        query = settings.insert().values(key=key, value=value)
        migrate_engine.execute(query)

def downgrade(migrate_engine):
    metadata.bind = migrate_engine
    for key, value in SETTINGS:
        query = settings.delete().where(settings.c.key == key)
        migrate_engine.execute(query)
