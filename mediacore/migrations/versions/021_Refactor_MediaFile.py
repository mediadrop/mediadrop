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

media_files = Table('media_files', metadata,
    Column('id', Integer, autoincrement=True, primary_key=True),
    Column('media_id', Integer, ForeignKey('media.id', onupdate='CASCADE', ondelete='CASCADE'), nullable=False),
    Column('storage_id', Integer, ForeignKey('storage.id', onupdate='CASCADE', ondelete='CASCADE')),

    Column('type', Unicode(16), nullable=False),
    Column('container', Unicode(10), nullable=False),
    Column('display_name', Unicode(255), nullable=False),
    Column('file_name', Unicode(255)),
    Column('http_url', Unicode(255)),
    Column('embed', Unicode(50)),
    Column('size', Integer),

    Column('created_on', DateTime, default=datetime.now, nullable=False),
    Column('modified_on', DateTime, default=datetime.now, onupdate=datetime.now, nullable=False),

    Column('rtmp_stream_url', Unicode(255)),
    Column('rtmp_file_name', Unicode(255)),
    Column('max_bitrate', Integer),
    Column('width', Integer),
    Column('height', Integer),

    mysql_engine='InnoDB',
    mysql_charset='utf8',
)

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

LOCAL_FILE_ENGINE = 'LocalFileStorage'
REMOTE_URL_ENGINE = 'RemoteURLStorage'
EMBED_ENGINES = {
    'google': 'GoogleVideoStorage',
    'vimeo': 'VimeoStorage',
    'youtube': 'YoutubeStorage',
}

def upgrade(migrate_engine):
    metadata.bind = migrate_engine
    conn = migrate_engine.connect()
    transaction = conn.begin()
    try:
        media_files.c.container.alter(nullable=True)
        media_files.c.storage_id.create()
        combine_unique_ids(conn)
        transaction.commit()
    except:
        transaction.rollback()
        raise

    media_files.c.storage_id.alter(nullable=False)
    media_files.c.file_name.alter(name='unique_id')
    media_files.c.http_url.drop()
    media_files.c.embed.drop()
    media_files.c.rtmp_stream_url.drop()
    media_files.c.rtmp_file_name.drop()

def combine_unique_ids(conn):
    engine_ids = fetch_engines(conn)
    local_engine_id = engine_ids[LOCAL_FILE_ENGINE]
    remote_engine_id = engine_ids[REMOTE_URL_ENGINE]
    rtmp_server_uris = set()
    embed_engine_ids = dict(
        (container, engine_ids[engine_type])
        for container, engine_type in EMBED_ENGINES.iteritems()
    )

    query = select([
        media_files.c.id,
        media_files.c.file_name,
        media_files.c.http_url,
        media_files.c.embed,
        media_files.c.container,
        media_files.c.rtmp_stream_url,
        media_files.c.rtmp_file_name,
    ])
    updates = []

    for file_id, file_name, http_url, embed, container, rtmp_server_url, rtmp_file_name in conn.execute(query):
        if file_name:
            q = media_files.update()\
                .where(media_files.c.id == file_id)\
                .values(storage_id=local_engine_id)
        elif http_url:
            q = media_files.update()\
                .where(media_files.c.id == file_id)\
                .values(storage_id=remote_engine_id,
                        file_name=http_url)
        elif embed:
            q = media_files.update()\
                .where(media_files.c.id == file_id)\
                .values(storage_id=embed_engine_ids[container],
                        file_name=embed,
                        container=None)
        elif rtmp_file_name:
            rtmp_server_uris.add(rtmp_server_url)
            q = media_files.update()\
                .where(media_files.c.id == file_id)\
                .values(storage_id=remote_engine_id,
                        file_name=rtmp_file_name)
        updates.append(q)

    if rtmp_server_uris:
        conn.execute(storage.update()\
            .where(storage.c.id == remote_engine_id)\
            .values(pickled_data={'rtmp_server_uris': list(rtmp_server_uris)}))

    for q in updates:
        conn.execute(q)

def fetch_engines(conn):
    query = select([storage.c.engine_type, storage.c.id])
    return dict(list(conn.execute(query)))

def downgrade(migrate_engine):
    raise NotImplementedError
