# This file is a part of MediaDrop (http://www.mediadrop.net),
# Copyright 2009-2013 MediaCore Inc., Felix Schwarz and other contributors.
# For the exact contribution history, see the git revision log.
# The source code contained in this file is licensed under the GPLv3 or
# (at your option) any later version.
# See LICENSE.txt in the main project directory, for more information.

from sqlalchemy import *
from migrate import *
from migrate.changeset.schema import ChangesetColumn

metadata = MetaData()
from datetime import datetime
VIDEO, AUDIO, AUDIO_DESC, CAPTIONS = 'video', 'audio', 'audio_desc', 'captions'

def get_new_columns():
    new_columns = (
        Column('rtmp_stream_url', Unicode(255)),
        Column('rtmp_file_name', Unicode(255)),
        Column('max_bitrate', Integer),
        Column('width', Integer),
        Column('height', Integer),
    )
    return new_columns

media_files_old = Table('media_files', metadata,
    Column('id', Integer, autoincrement=True, primary_key=True),
    Column('media_id', Integer, ForeignKey('media.id', onupdate='CASCADE', ondelete='CASCADE'), nullable=False),

    Column('type', Enum(VIDEO, AUDIO, AUDIO_DESC, CAPTIONS), nullable=False),
    Column('container', Unicode(10), nullable=False),
    Column('display_name', Unicode(255), nullable=False),
    Column('file_name', Unicode(255)),
    Column('http_url', Unicode(255)),
    Column('embed', Unicode(50)),
    Column('size', Integer),
    Column('created_on', DateTime, default=datetime.now, nullable=False),
    Column('modified_on', DateTime, default=datetime.now, onupdate=datetime.now, nullable=False),

    mysql_engine='InnoDB',
    mysql_charset='utf8',
)

def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind migrate_engine
    # to your metadata

    # Create all of the new columns on the media_files table
    metadata.bind = migrate_engine
    for col in get_new_columns():
        col.create(media_files_old)

def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.

    # Drop all of the new columns from the media_files table.
    metadata.bind = migrate_engine
    for col in get_new_columns():
        col.drop(media_files_old)

