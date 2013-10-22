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

groups_permissions = Table('groups_permissions', metadata,
    Column('group_id', Integer, ForeignKey('groups.group_id',
        onupdate="CASCADE", ondelete="CASCADE")),
    Column('permission_id', Integer, ForeignKey('permissions.permission_id',
        onupdate="CASCADE", ondelete="CASCADE")),
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

def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind migrate_engine
    # to your metadata
    metadata.bind = migrate_engine
    conn = migrate_engine.connect()

    admins_group_id = select(
        [groups.c.group_id],
        groups.c.group_name == u'Admins',
    ).scalar()

    if admins_group_id is None:
        raise ValueError("You've been messing with auth permissions haven't you? "
                         "You can skip this migration if you wish, by manually "
                         "incrementing the version num in the migration_version "
                         "table by 1. Be aware that you'll need an 'edit' "
                         "permission to access most admin panels, however.")

    edit_perm_id = conn.execute(permissions.insert().values(
        permission_name=u'edit',
        description=u'Grants access to edit site content',
    )).inserted_primary_key[0]

    editors_group_id = conn.execute(groups.insert().values(
        group_name=u'editors',
        display_name=u'Editors',
    )).inserted_primary_key[0]

    conn.execute(groups_permissions.insert().values(
        group_id=admins_group_id,
        permission_id=edit_perm_id,
    ))

    conn.execute(groups_permissions.insert().values(
        group_id=editors_group_id,
        permission_id=edit_perm_id,
    ))

def downgrade(migrate_engine):
    raise NotImplementedError()
