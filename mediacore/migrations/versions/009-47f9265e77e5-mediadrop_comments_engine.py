# This file is a part of MediaDrop (http://www.mediadrop.net),
# Copyright 2009-2013 MediaDrop contributors
# For the exact contribution history, see the git revision log.
# The source code contained in this file is licensed under the GPLv3 or
# (at your option) any later version.
# See LICENSE.txt in the main project directory, for more information.
"""MediaDrop comments engine

replace the comments engine settings value 'mediacore' with 'builtin'

added: 2013-11-01 (v0.11dev)

Revision ID: 47f9265e77e5
Revises: 4c9f4cfc6085
Create Date: 2013-11-01 10:15:02.948019
"""

# revision identifiers, used by Alembic.
revision = '47f9265e77e5'
down_revision = '4c9f4cfc6085'

from alembic.op import execute, inline_literal
from sqlalchemy import and_
from sqlalchemy.types import Integer, Unicode, UnicodeText
from sqlalchemy.schema import Column, MetaData, Table

# -- table definition ---------------------------------------------------------
metadata = MetaData()
settings = Table('settings', metadata,
    Column('id', Integer, autoincrement=True, primary_key=True),
    Column('key', Unicode(255), nullable=False, unique=True),
    Column('value', UnicodeText),
    mysql_engine='InnoDB',
    mysql_charset='utf8',
)

# -----------------------------------------------------------------------------

def upgrade():
    update_setting(u'comments_engine', u'mediacore', u'builtin')

def downgrade():
    update_setting(u'comments_engine', u'builtin', u'mediacore')


# -- helpers ------------------------------------------------------------------

def update_setting(key, current_value, new_value):
    execute(
        settings.update().\
            where(and_(
                settings.c.key == key,
                settings.c.value == current_value)).\
            values({
                'value': inline_literal(new_value),
            })
    )

