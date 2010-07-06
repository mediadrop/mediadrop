from sqlalchemy import *
from migrate import *

SETTING_KEY = u'use_embed_thumbnails'
DEFAULT_VALUE = u'true'

metadata = MetaData()
settings = Table('settings', metadata,
    Column('id', Integer, autoincrement=True, primary_key=True),
    Column('key', Unicode(255), nullable=False, unique=True),
    Column('value', UnicodeText),
    mysql_engine='InnoDB',
    mysql_charset='utf8',
)

def upgrade(migrate_engine):
    query = settings.insert().values(key=SETTING_KEY, value=DEFAULT_VALUE)
    migrate_engine.execute(query)

def downgrade(migrate_engine):
    query = settings.delete().where(settings.c.key == SETTING_KEY)
    migrate_engine.execute(query)
