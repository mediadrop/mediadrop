# This file is a part of MediaCore CE, Copyright 2009-2012 MediaCore Inc.
# The source code contained in this file is licensed under the GPL.
# See LICENSE.txt in the main project directory, for more information.

from sqlalchemy import *
from migrate import *

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
    query = settings.update()\
                    .where(settings.c.key==u'wording_additional_notes')\
                    .values(key=u'wording_administrative_notes')
    migrate_engine.execute(query)

def downgrade(migrate_engine):
    metadata.bind = migrate_engine
    query = settings.update()\
                    .where(settings.c.key==u'wording_administrative_notes')\
                    .values(key=u'wording_additional_notes')
    migrate_engine.execute(query)
