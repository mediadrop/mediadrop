import cPickle

from datetime import datetime

from sqlalchemy import *
from migrate import *

metadata = MetaData()
storage = Table('storage', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('engine_type', Unicode(30), nullable=False),
    Column('display_name', Unicode(100), nullable=False, unique=True),
    Column('pickled_data', PickleType, nullable=False),
    Column('is_primary', Boolean, nullable=False, default=False),
    Column('created_on', DateTime, nullable=False, default=datetime.now),
    Column('modified_on', DateTime, nullable=False, default=datetime.now,
                                                    onupdate=datetime.now),
    mysql_engine='InnoDB',
    mysql_charset='utf8',
)

def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind migrate_engine
    # to your metadata
    metadata.bind = migrate_engine
    connection = migrate_engine.connect()
    storage.c.is_primary.alter(name='enabled')
    connection.execute(storage.update().values(enabled=True))

def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    metadata.bind = migrate_engine
    storage.c.enabled.alter(name='is_primary')
