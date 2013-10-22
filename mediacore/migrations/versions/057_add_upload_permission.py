# This file is a part of MediaDrop (http://www.mediadrop.net),
# Copyright 2009-2013 MediaCore Inc., Felix Schwarz and other contributors.
# For the exact contribution history, see the git revision log.
# The source code contained in this file is licensed under the GPLv3 or
# (at your option) any later version.
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

permissions = Table('permissions', metadata,
    Column('permission_id', Integer, autoincrement=True, primary_key=True),
    Column('permission_name', Unicode(16), unique=True, nullable=False),
    Column('description', Unicode(255)),
    mysql_engine='InnoDB',
    mysql_charset='utf8',
)

groups_permissions = Table('groups_permissions', metadata,
    Column('group_id', Integer, ForeignKey('groups.group_id',
        onupdate="CASCADE", ondelete="CASCADE")),
    Column('permission_id', Integer, ForeignKey('permissions.permission_id',
        onupdate="CASCADE", ondelete="CASCADE")),
    mysql_engine='InnoDB',
    mysql_charset='utf8',
)


group_names = [u'anonymous', u'admins', u'editors']


def upgrade(migrate_engine):
    query = permissions.insert().values(permission_name=u'upload', description=u'Can upload new media')
    migrate_engine.execute(query)
    
    for group_name in group_names:
        group_id_subquery = select([groups.c.group_id]).where(groups.c.group_name == group_name)
        permission_id_subquery = select([permissions.c.permission_id]).where(permissions.c.permission_name == u'upload')
        query = groups_permissions.insert().values(
            group_id=group_id_subquery,
            permission_id=permission_id_subquery
        )
        migrate_engine.execute(query)

def downgrade(migrate_engine):
    query = permissions.delete().where(permissions.c.permission_name==u'upload')
    migrate_engine.execute(query)
    
    for group_name in group_names:
        group_id_subquery = select([groups.c.group_id]).where(groups.c.group_name == group_name)
        permission_id_subquery = select([permissions.c.permission_id]).where(permissions.c.permission_name == u'upload')
        query = groups_permissions.delete().where(and_(
            groups_permissions.c.group_id == group_id_subquery,
            groups_permissions.c.permission_id == permission_id_subquery
        ))
        migrate_engine.execute(query)

