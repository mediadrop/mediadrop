# This file is a part of MediaDrop (http://www.mediadrop.net),
# Copyright 2009-2013 MediaCore Inc., Felix Schwarz and other contributors.
# For the exact contribution history, see the git revision log.
# The source code contained in this file is licensed under the GPLv3 or
# (at your option) any later version.
# See LICENSE.txt in the main project directory, for more information.

import cPickle
import simplejson

from datetime import datetime

from sqlalchemy import *
from sqlalchemy.types import TypeDecorator
from migrate import *

class Json(TypeDecorator):
    impl = Text

    def process_bind_param(self, value, dialect):
        return simplejson.dumps(value)

    def process_result_value(self, value, dialect):
        return simplejson.loads(value)

metadata = MetaData()
storage = Table('storage', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('engine_type', Unicode(30), nullable=False),
    Column('display_name', Unicode(100), nullable=False, unique=True),
    Column('pickled_data', PickleType, nullable=False),
    Column('data', Json, nullable=False),
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
    storage.c.data.create()
    transaction.commit()

    query = select([
        storage.c.id,
        storage.c.pickled_data,
    ])

    transaction = connection.begin()
    for storage_id, data in connection.execute(query):
        connection.execute(storage.update()\
            .where(storage.c.id == storage_id)\
            .values(data=data))
    transaction.commit()

    transaction = connection.begin()
    storage.c.pickled_data.drop()
    transaction.commit()

def downgrade(migrate_engine):
    raise NotImplementedError()
