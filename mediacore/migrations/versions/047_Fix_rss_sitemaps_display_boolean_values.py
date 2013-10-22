# This file is a part of MediaDrop (http://www.mediadrop.net),
# Copyright 2009-2013 MediaCore Inc., Felix Schwarz and other contributors.
# For the exact contribution history, see the git revision log.
# The source code contained in this file is licensed under the GPLv3 or
# (at your option) any later version.
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

    for setting_key in (u'rss_display', u'sitemaps_display'):
        query = select([settings.c.value]).\
            where(settings.c.key == setting_key)
        value = conn.execute(query).scalar()

        if value == 'enabled':
            new_value = u'True'
        else:
            new_value = u''

        update = settings.update()\
            .where(settings.c.key == setting_key)\
            .values(value=new_value)
        conn.execute(update)

def downgrade(migrate_engine):
    metadata.bind = migrate_engine
    raise NotImplementedError()
