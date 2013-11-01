# This file is a part of MediaDrop (http://www.mediadrop.net),
# Copyright 2009-2013 MediaDrop contributors
# For the exact contribution history, see the git revision log.
# The source code contained in this file is licensed under the GPLv3 or
# (at your option) any later version.
# See LICENSE.txt in the main project directory, for more information.
"""rename MediaCore settings

added: 2013-11-01 (v0.11dev)

Revision ID: e1488bb4dd
Revises: 47f9265e77e5
Create Date: 2013-11-01 10:28:04.982852
"""

# revision identifiers, used by Alembic.
revision = 'e1488bb4dd'
down_revision = '47f9265e77e5'

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
    update_setting(u'general_site_name', u'MediaCore', u'MediaDrop')
    update_settings_key(
        u'appearance_display_mediacore_footer',
        u'appearance_display_mediadrop_footer')
    update_settings_key(
        u'appearance_display_mediacore_credits',
        u'appearance_display_mediadrop_credits')

def downgrade():
    update_setting(u'general_site_name', u'MediaDrop', u'MediaCore')
    update_settings_key(
        u'appearance_display_mediadrop_footer',
        u'appearance_display_mediacore_footer')
    update_settings_key(
        u'appearance_display_mediadrop_credits',
        u'appearance_display_mediacore_credits')


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

def update_settings_key(current_key, new_key):
    execute(
        settings.update().\
            where(and_(
                settings.c.key == current_key,
            )).\
            values({
                'key': inline_literal(new_key),
            })
    )

