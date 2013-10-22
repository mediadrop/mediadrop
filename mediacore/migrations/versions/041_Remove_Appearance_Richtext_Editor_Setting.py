# This file is a part of MediaDrop (http://www.mediadrop.net),
# Copyright 2009-2013 MediaCore Inc., Felix Schwarz and other contributors.
# For the exact contribution history, see the git revision log.
# The source code contained in this file is licensed under the GPLv3 or
# (at your option) any later version.
# See LICENSE.txt in the main project directory, for more information.

from sqlalchemy import *
from migrate import *

SETTINGS = [
    (u'appearance_enable_rich_text', u'true'),
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
        query = settings.delete().where(settings.c.key==key)
        migrate_engine.execute(query)

def downgrade(migrate_engine):
    metadata.bind = migrate_engine
    for key, value in SETTINGS:
        query = settings.insert.values(key=key, value=value)
        migrate_engine.execute(query)
