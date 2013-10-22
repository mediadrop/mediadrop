# This file is a part of MediaDrop (http://www.mediadrop.net),
# Copyright 2009-2013 MediaCore Inc., Felix Schwarz and other contributors.
# For the exact contribution history, see the git revision log.
# The source code contained in this file is licensed under the GPLv3 or
# (at your option) any later version.
# See LICENSE.txt in the main project directory, for more information.

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
        NAME: 'Local File Storage',
        DATA: cPickle.dumps({}, cPickle.HIGHEST_PROTOCOL),
        PRIMARY: True,
    },
    {
        TYPE: 'RemoteURLStorage',
        NAME: 'Remote URLs',
        DATA: cPickle.dumps({}, cPickle.HIGHEST_PROTOCOL),
        PRIMARY: False,
    },
    {
        TYPE: 'YoutubeStorage',
        NAME: 'YouTube',
        DATA: cPickle.dumps({}, cPickle.HIGHEST_PROTOCOL),
        PRIMARY: False,
    },
    {
        TYPE: 'VimeoStorage',
        NAME: 'Vimeo',
        DATA: cPickle.dumps({}, cPickle.HIGHEST_PROTOCOL),
        PRIMARY: False,
    },
    {
        TYPE: 'GoogleVideoStorage',
        NAME: 'Google Video',
        DATA: cPickle.dumps({}, cPickle.HIGHEST_PROTOCOL),
        PRIMARY: False,
    },
    {
        TYPE: 'BlipTVStorage',
        NAME: 'BlipTV',
        DATA: cPickle.dumps({}, cPickle.HIGHEST_PROTOCOL),
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
