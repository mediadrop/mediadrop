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

SETTING_KEY = u'req_comment_approval'

def upgrade(migrate_engine):
    metadata.bind = migrate_engine
    conn = migrate_engine.connect()

    query = select([settings.c.value]).\
        where(settings.c.key == SETTING_KEY)
    current_value = conn.execute(query).scalar()

    if current_value == u'true':
        new_value = u'True'
    else:
        new_value = u''

    query = settings.update().where(settings.c.key == SETTING_KEY).\
        values(value=new_value)
    conn.execute(query)

def downgrade(migrate_engine):
    metadata.bind = migrate_engine
