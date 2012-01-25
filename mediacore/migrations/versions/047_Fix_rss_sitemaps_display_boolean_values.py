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
    conn = migrate_engine.connect()

    for setting_key in ('rss_display', 'sitemaps_display'):
        query = select([settings.c.value]).\
            where(settings.c.key == setting_key)
        value = conn.execute(query).scalar()

        if value == 'enabled':
            new_value = 'True'
        else:
            new_value = ''

        update = settings.update()\
            .where(settings.c.key == setting_key)\
            .values(value=new_value)
        conn.execute(update)

def downgrade(migrate_engine):
    metadata.bind = migrate_engine
    raise NotImplementedError()
