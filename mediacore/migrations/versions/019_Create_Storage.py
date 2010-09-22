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

TYPE, NAME, DATA, PRIMARY = 'type', 'name', 'data', 'primary'

DEFAULT_ENGINES = [
    {
        TYPE: 'LocalFileStorage',
        NAME: 'Default File Storage',
        DATA: cPickle.dumps({}),
        PRIMARY: True,
    },
    {
        TYPE: 'YoutubeStorage',
        NAME: 'YouTube',
        DATA: cPickle.dumps({}),
        PRIMARY: False,
    },
    {
        TYPE: 'VimeoStorage',
        NAME: 'Vimeo',
        DATA: cPickle.dumps({}),
        PRIMARY: False,
    },
    {
        TYPE: 'GoogleVideoStorage',
        NAME: 'Google Video',
        DATA: cPickle.dumps({}),
        PRIMARY: False,
    },
    {
        TYPE: 'RemoteURLStorage',
        NAME: 'Default URL Handler',
        DATA: cPickle.dumps({}),
        PRIMARY: False,
    },
]

def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind migrate_engine
    # to your metadata
    metadata.bind = migrate_engine
    storage.create()
    conn = migrate_engine.connect()
    insert = storage.insert().values(
        engine_type=bindparam(TYPE),
        display_name=bindparam(NAME),
        pickled_data=bindparam(DATA),
        is_primary=bindparam(PRIMARY),
    )
    conn.execute(insert, DEFAULT_ENGINES)

def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    metadata.bind = migrate_engine
    storage.drop()
