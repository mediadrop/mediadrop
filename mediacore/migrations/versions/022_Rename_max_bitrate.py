from sqlalchemy import *
from migrate import *

metadata = MetaData()

media_files = Table('media_files', metadata,
    Column('id', Integer, autoincrement=True, primary_key=True),
    Column('max_bitrate', Integer),
    mysql_engine='InnoDB',
    mysql_charset='utf8',
)

def upgrade(migrate_engine):
    metadata.bind = migrate_engine
    conn = migrate_engine.connect()
    media_files.c.max_bitrate.alter(name='bitrate')

def downgrade(migrate_engine):
    metadata.bind = migrate_engine
    conn = migrate_engine.connect()
    media_files.c.bitrate.alter(name='max_bitrate')
