# This file is a part of MediaCore CE, Copyright 2009-2012 MediaCore Inc.
# The source code contained in this file is licensed under the GPL.
# See LICENSE.txt in the main project directory, for more information.

from datetime import datetime

from sqlalchemy import *
from migrate import *

metadata = MetaData()
groups = Table('groups', metadata,
    Column('group_id', Integer, autoincrement=True, primary_key=True),
    Column('group_name', Unicode(16), unique=True, nullable=False),
    Column('display_name', Unicode(255)),
    Column('created', DateTime, default=datetime.now),
    mysql_engine='InnoDB',
    mysql_charset='utf8',
)


new_groups = (
    dict(group_name=u'anonymous', display_name=u'Everyone (including guests)'),
    dict(group_name=u'authenticated', display_name=u'Logged in users'),
)

def upgrade(migrate_engine):
    for group_attributes in new_groups:
        query = groups.insert().values(**group_attributes)
        migrate_engine.execute(query)

def downgrade(migrate_engine):
    for group_attributes in new_groups:
        group_name = group_attributes['group_name']
        query = groups.delete().where(groups.c.group_name == group_name)
        migrate_engine.execute(query)
    # assignments of users to 'anonymous' and 'authenticated' are deleted 
    # automatically

