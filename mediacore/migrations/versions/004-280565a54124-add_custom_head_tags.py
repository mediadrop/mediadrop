# This file is a part of MediaDrop (http://www.mediadrop.net),
# Copyright 2009-2013 MediaDrop contributors
# For the exact contribution history, see the git revision log.
# The source code contained in this file is licensed under the GPLv3 or
# (at your option) any later version.
# See LICENSE.txt in the main project directory, for more information.
"""add custom head tags

add setting for custom tags (HTML) in <head> section

added: 2012-02-13 (v0.10dev)
previously migrate script v054

Revision ID: 280565a54124
Revises: 4d27ff5680e5
Create Date: 2013-05-14 22:38:02.552230
"""

# revision identifiers, used by Alembic.
revision = '280565a54124'
down_revision = '4d27ff5680e5'

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

SETTINGS = [
    (u'appearance_custom_head_tags', u''),
]

def upgrade():
    for key, value in SETTINGS:
        insert_setting(key, value)

def downgrade():
    for key, value in SETTINGS:
        delete_setting(key)

