# This file is a part of MediaCore CE, Copyright 2009-2012 MediaCore Inc.
# The source code contained in this file is licensed under the GPL.
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
    Column('enabled', Boolean, nullable=False, default=True),
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

    transaction = connection.begin()
    storage.c.is_primary.alter(name='enabled')
    transaction.commit()

    transaction = connection.begin()
    connection.execute(storage.update().values(enabled=True))
    transaction.commit()

def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    metadata.bind = migrate_engine
    storage.c.enabled.alter(name='is_primary')
