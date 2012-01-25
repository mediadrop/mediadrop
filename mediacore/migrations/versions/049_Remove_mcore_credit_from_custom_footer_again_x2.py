# This file is a part of MediaCore CE, Copyright 2009-2012 MediaCore Inc.
# The source code contained in this file is licensed under the GPL.
# See LICENSE.txt in the main project directory, for more information.

from sqlalchemy import *
from migrate import *

metadata = MetaData()
settings = Table('settings', metadata,
    Column('id', Integer, autoincrement=True, primary_key=True),
    Column('key', Unicode(255), nullable=False, unique=True),
    Column('value', UnicodeText),
    mysql_engine='InnoDB',
    mysql_charset='utf8',
)

FOOTER_SETTING_KEY = u'appearance_custom_footer_html'
DEFAULT_FOOTER_VALUE = u'<!--! If you remove this link, please' \
        + 'consider adding another link somewhere on your site. --> <p>powered' \
        + 'by <a href="http://getmediacore.com/">MediaCore'  \
        + 'Video Platform</a></p>'

def upgrade(migrate_engine):
    metadata.bind = migrate_engine
    conn = migrate_engine.connect()
    query = select([settings.c.value]).\
        where(settings.c.key == FOOTER_SETTING_KEY)
    current_footer_value = conn.execute(query).scalar()
    if current_footer_value == DEFAULT_FOOTER_VALUE:
        query = settings.update().where(settings.c.key == FOOTER_SETTING_KEY).\
            values(value=u'')
        conn.execute(query)

def downgrade(migrate_engine):
    metadata.bind = migrate_engine
