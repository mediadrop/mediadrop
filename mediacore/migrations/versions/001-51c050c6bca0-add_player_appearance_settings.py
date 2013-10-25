# This file is a part of MediaDrop (http://www.mediadrop.net),
# Copyright 2009-2013 MediaDrop contributors
# For the exact contribution history, see the git revision log.
# The source code contained in this file is licensed under the GPLv3 or
# (at your option) any later version.
# See LICENSE.txt in the main project directory, for more information.
"""Add player appearance settings

add configuration settings for buttons on the player bar

added: 2011-02-07 (v0.9.1)
previously migrate script v051

Revision ID: 51c050c6bca0
Revises: 50258ad7a96d
Create Date: 2013-05-14 22:35:41.914345
"""

# revision identifiers, used by Alembic.
revision = '51c050c6bca0'
down_revision = '50258ad7a96d'

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
    (u'appearance_show_download', u'True'),
    (u'appearance_show_share', u'True'),
    (u'appearance_show_embed', u'True'),
    (u'appearance_show_widescreen', u'True'),
    (u'appearance_show_popout', u'True'),
    (u'appearance_show_like', u'True'),
    (u'appearance_show_dislike', u'True'),
]

def upgrade():
    for key, value in SETTINGS:
        insert_setting(key, value)

def downgrade():
    for key, value in SETTINGS:
        delete_setting(key)
