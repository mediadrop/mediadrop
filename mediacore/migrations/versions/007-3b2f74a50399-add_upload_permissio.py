# This file is a part of MediaDrop (http://www.mediadrop.net),
# Copyright 2009-2013 MediaDrop contributors
# For the exact contribution history, see the git revision log.
# The source code contained in this file is licensed under the GPLv3 or
# (at your option) any later version.
# See LICENSE.txt in the main project directory, for more information.
"""add upload permission

added: 2012-12-22 (v0.10dev)
previously migrate script v057

Revision ID: 3b2f74a50399
Revises: 30bb0d88d139
Create Date: 2013-05-14 22:38:42.221082
"""

# revision identifiers, used by Alembic.
revision = '3b2f74a50399'
down_revision = '30bb0d88d139'

from datetime import datetime

from alembic.op import execute, inline_literal
from sqlalchemy import Column, MetaData, Table
from sqlalchemy import and_, DateTime, ForeignKey, Integer, Unicode, UnicodeText
from sqlalchemy.sql import select

# -- table definition ---------------------------------------------------------
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

# -- helpers ------------------------------------------------------------------
def insert_permission(permission_name, description):
    execute(
        permissions.insert().\
            values({
                'permission_name': inline_literal(permission_name),
                'description': inline_literal(description),
            })
    )

def delete_permission(permission_name):
    execute(
        permissions.delete().\
            where(permissions.c.permission_name==inline_literal(permission_name))
    )

def grant_permission_for_group(permission_name, group_name):
    execute(
        groups_permissions.insert().values(
            group_id=select([groups.c.group_id]).where(groups.c.group_name == group_name),
            permission_id=select([permissions.c.permission_id]).where(permissions.c.permission_name == permission_name)
        )
    )

def revoke_permission_for_group(permission_name, group_name):
    group_subquery = select([groups.c.group_id]).\
        where(groups.c.group_name == group_name)
    permission_subquery = select([permissions.c.permission_id]).\
        where(permissions.c.permission_name == permission_name)
    
    execute(
        groups_permissions.delete().where(and_(
            groups_permissions.c.group_id == group_subquery,
            groups_permissions.c.permission_id == permission_subquery
        ))
    )

# -----------------------------------------------------------------------------


GROUP_NAMES = [u'anonymous', u'admins', u'editors']

def upgrade():
    insert_permission(u'upload', u'Can upload new media')
    for group_name in GROUP_NAMES:
        grant_permission_for_group(u'upload', group_name)

def downgrade():
    for group_name in GROUP_NAMES:
        revoke_permission_for_group(u'upload', group_name)
    delete_permission(u'upload')

