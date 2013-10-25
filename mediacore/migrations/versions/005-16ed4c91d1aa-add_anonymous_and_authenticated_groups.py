# This file is a part of MediaDrop (http://www.mediadrop.net),
# Copyright 2009-2013 MediaDrop contributors
# For the exact contribution history, see the git revision log.
# The source code contained in this file is licensed under the GPLv3 or
# (at your option) any later version.
# See LICENSE.txt in the main project directory, for more information.
"""add anonymous and authenticated groups

create groups for "anonymous" and "authenticated" users

added: 2012-12-11 (v0.10dev)
previously migrate script v055

Revision ID: 16ed4c91d1aa
Revises: 280565a54124
Create Date: 2013-05-14 22:38:25.194543
"""

# revision identifiers, used by Alembic.
revision = '16ed4c91d1aa'
down_revision = '280565a54124'

from datetime import datetime

from alembic.op import execute, inline_literal
from sqlalchemy import Column, MetaData, Table
from sqlalchemy import DateTime, ForeignKey, Integer, Unicode, UnicodeText

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


def add_group(group_name, display_name):
    execute(
        groups.insert().\
            values({
                'group_name': inline_literal(group_name),
                'display_name': inline_literal(display_name),
            })
    )

def upgrade():
    add_group(group_name=u'anonymous', display_name=u'Everyone (including guests)')
    add_group(group_name=u'authenticated', display_name=u'Logged in users')

def downgrade():
    execute(
        groups.delete().\
            where(groups.c.group_name.in_([u'anonymous', u'authenticated']))
    )
    # assignments of users to 'anonymous' and 'authenticated' are deleted 
    # automatically because of existing ForeignKey constraint in the DB
    # (ON DELETE CASCADE ON UPDATE CASCADE)

