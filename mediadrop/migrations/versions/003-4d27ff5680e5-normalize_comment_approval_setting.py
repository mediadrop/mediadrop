# This file is a part of MediaDrop (http://www.mediadrop.net),
# Copyright 2009-2013 MediaDrop contributors
# For the exact contribution history, see the git revision log.
# The source code contained in this file is licensed under the GPLv3 or
# (at your option) any later version.
# See LICENSE.txt in the main project directory, for more information.
"""Normalize comment approval setting

normalize value for comment approval setting so that it can be used a boolean 
directly. This migration can not be run offline.

added: 2011-03-13 (v0.9.1)
previously migrate script v053

Revision ID: 4d27ff5680e5
Revises: 432df7befe8d
Create Date: 2013-05-14 22:36:27.130301
"""

# revision identifiers, used by Alembic.
revision = '4d27ff5680e5'
down_revision = '432df7befe8d'

from alembic import context
from alembic.op import execute, inline_literal
from sqlalchemy import Integer, Unicode, UnicodeText
from sqlalchemy import Column, MetaData,  Table

# -- table definition ---------------------------------------------------------
metadata = MetaData()
settings = Table('settings', metadata,
    Column('id', Integer, autoincrement=True, primary_key=True),
    Column('key', Unicode(255), nullable=False, unique=True),
    Column('value', UnicodeText),
    mysql_engine='InnoDB',
    mysql_charset='utf8',
)

# -- helpers ------------------------------------------------------------------
def insert_setting(key, value):
    execute(
        settings.insert().\
            values({
                'key': inline_literal(key),
                'value': inline_literal(value),
            })
    )

def delete_setting(key):
    execute(
        settings.delete().\
            where(settings.c.key==inline_literal(key))
    )
# -----------------------------------------------------------------------------

SETTING_KEY = u'req_comment_approval'


def upgrade():
    if context.is_offline_mode():
        raise AssertionError('This migration can not be run in offline mode.')
    connection = context.get_context().connection
    query = settings.select(settings.c.key == SETTING_KEY)
    result = connection.execute(query).fetchone()
    
    current_value = result.value
    if current_value == u'true':
        new_value = u'True'
    else:
        new_value = u''
    execute(
        settings.update().\
            where(settings.c.key==inline_literal(SETTING_KEY)).\
            values({
                'value': inline_literal(new_value),
            })
    )

def downgrade():
    # no action necessary
    pass
