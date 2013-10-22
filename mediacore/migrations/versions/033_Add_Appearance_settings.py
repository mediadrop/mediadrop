# This file is a part of MediaDrop (http://www.mediadrop.net),
# Copyright 2009-2013 MediaCore Inc., Felix Schwarz and other contributors.
# For the exact contribution history, see the git revision log.
# The source code contained in this file is licensed under the GPLv3 or
# (at your option) any later version.
# See LICENSE.txt in the main project directory, for more information.

from sqlalchemy import *
from migrate import *

SETTINGS = [
    (u'appearance_logo', u''),
    (u'appearance_background_image', u''),
    (u'appearance_background_color', u'#fff'),
    (u'appearance_link_color', u'#0f7cb4'),
    (u'appearance_visited_link_color', u'#0f7cb4'),
    (u'appearance_text_color', u'#637084'),
    (u'appearance_heading_color', u'#3f3f3f'),
    (u'appearance_navigation_bar_color', u'purple'),
    (u'appearance_enable_featured_items', u'True'),
    (u'appearance_enable_podcast_tab', u'True'),
    (u'appearance_enable_user_uploads', u'True'),
    (u'appearance_enable_rich_text', u'True'),
    (u'appearance_display_logo', u'True'),
    (u'appearance_display_background_image', u'True'),
    (u'appearance_custom_css', u''),
    (u'appearance_custom_header_html', u''),
    (u'appearance_custom_footer_html', u'<!--! If you remove this link, please' \
        + 'consider adding another link somewhere on your site. --> <p>powered' \
        + 'by <a href="http://getmediacore.com/">MediaCore'  \
        + 'Video Platform</a></p>'),
]

metadata = MetaData()
settings = Table('settings', metadata,
    Column('id', Integer, autoincrement=True, primary_key=True),
    Column('key', Unicode(255), nullable=False, unique=True),
    Column('value', UnicodeText),
    mysql_engine='InnoDB',
    mysql_charset='utf8',
)

def upgrade(migrate_engine):
    metadata.bind = migrate_engine
    for key, value in SETTINGS:
        query = settings.insert().values(key=key, value=value)
        migrate_engine.execute(query)

def downgrade(migrate_engine):
    metadata.bind = migrate_engine
    for key, value in SETTINGS:
        query = settings.delete().where(settings.c.key == key)
        migrate_engine.execute(query)
