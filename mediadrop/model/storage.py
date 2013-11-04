# This file is a part of MediaDrop (http://www.mediadrop.net),
# Copyright 2009-2013 MediaDrop contributors
# For the exact contribution history, see the git revision log.
# The source code contained in this file is licensed under the GPLv3 or
# (at your option) any later version.
# See LICENSE.txt in the main project directory, for more information.

import logging

from datetime import datetime

from sqlalchemy import Column, sql, Table
from sqlalchemy.orm import column_property, dynamic_loader, mapper
from sqlalchemy.types import Boolean, DateTime, Integer, Unicode

from mediadrop.lib.storage import StorageEngine
from mediadrop.model.media import MediaFile, MediaFileQuery, media_files
from mediadrop.model.meta import metadata
from mediadrop.model.util import JSONType

log = logging.getLogger(__name__)

storage = Table('storage', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('engine_type', Unicode(30), nullable=False),
    Column('display_name', Unicode(100), nullable=False, unique=True),
    Column('enabled', Boolean, nullable=False, default=True),
    Column('created_on', DateTime, nullable=False, default=datetime.now),
    Column('modified_on', DateTime, nullable=False, default=datetime.now,
                                                    onupdate=datetime.now),
    Column('data', JSONType, nullable=False, default=dict),
    mysql_engine='InnoDB',
    mysql_charset='utf8',
)

storage_mapper = mapper(
    StorageEngine, storage,
    polymorphic_on=storage.c.engine_type,
    properties={
        '_data': storage.c.data,

        # Avoid conflict with the abstract StorageEngine.engine_type property
        '_engine_type': storage.c.engine_type,

        # Make the storage engine available on MediaFile instances
        'files': dynamic_loader(
            MediaFile,
            backref='storage',
            query_class=MediaFileQuery,
            passive_deletes=True,
        ),
        'file_count': column_property(
            sql.select(
                [sql.func.count(media_files.c.id)],
                storage.c.id == media_files.c.storage_id,
            ).label('file_count'),
            deferred=True,
        ),
        'file_size_sum': column_property(
            sql.select(
                [sql.func.sum(media_files.c.size)],
                storage.c.id == media_files.c.storage_id,
            ).label('file_size_sum'),
            deferred=True,
        ),
    },
)

def add_engine_type(engine_cls):
    """Register this storage engine with the ORM."""
    log.debug('Registering engine %r: %r', engine_cls.engine_type, engine_cls)
    mapper(engine_cls,
           inherits=storage_mapper,
           polymorphic_identity=engine_cls.engine_type)

# Add our built-in storage engines to the polymorphic ORM mapping.
for engine in StorageEngine:
    add_engine_type(engine)

# Automatically add new engines as they're registered by plugins.
StorageEngine.add_register_observer(add_engine_type)
