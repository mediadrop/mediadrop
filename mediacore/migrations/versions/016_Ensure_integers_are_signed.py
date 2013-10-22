# This file is a part of MediaDrop (http://www.mediadrop.net),
# Copyright 2009-2013 MediaCore Inc., Felix Schwarz and other contributors.
# For the exact contribution history, see the git revision log.
# The source code contained in this file is licensed under the GPLv3 or
# (at your option) any later version.
# See LICENSE.txt in the main project directory, for more information.


from datetime import datetime

from sqlalchemy import *
from sqlalchemy.exc import OperationalError
from migrate import *

metadata = MetaData()

slug_length = 50
AUDIO = 'audio'
AUDIO_DESC = 'audio_desc'
VIDEO = 'video'
CAPTIONS = 'captions'

users = Table('users', metadata,
    Column('user_id', Integer, autoincrement=True, primary_key=True),
    Column('user_name', Unicode(16), unique=True, nullable=False),
    Column('email_address', Unicode(255), unique=True, nullable=False),
    Column('display_name', Unicode(255)),
    Column('password', Unicode(80)),
    Column('created', DateTime, default=datetime.now),
    mysql_engine='InnoDB',
    mysql_charset='utf8',
)
users_groups = Table('users_groups', metadata,
    Column('user_id', Integer),
    Column('group_id', Integer),
    ForeignKeyConstraint(['user_id'], ['users.user_id'], name='users_groups_ibfk_1',
        onupdate="CASCADE", ondelete="CASCADE"),
    ForeignKeyConstraint(['group_id'], ['groups.group_id'], name='users_groups_ibfk_2',
        onupdate="CASCADE", ondelete="CASCADE"),
    mysql_engine='InnoDB',
    mysql_charset='utf8',
)
groups = Table('groups', metadata,
    Column('group_id', Integer, autoincrement=True, primary_key=True),
    Column('group_name', Unicode(16), unique=True, nullable=False),
    Column('display_name', Unicode(255)),
    Column('created', DateTime, default=datetime.now),
    mysql_engine='InnoDB',
    mysql_charset='utf8',
)
groups_permissions = Table('groups_permissions', metadata,
    Column('group_id', Integer),
    Column('permission_id', Integer),
    ForeignKeyConstraint(['group_id'], ['groups.group_id'],
        name='groups_permissions_ibfk_1',
        onupdate="CASCADE", ondelete="CASCADE"),
    ForeignKeyConstraint(['permission_id'], ['permissions.permission_id'],
        name='groups_permissions_ibfk_2',
        onupdate="CASCADE", ondelete="CASCADE"),
    mysql_engine='InnoDB',
    mysql_charset='utf8',
)
permissions = Table('permissions', metadata,
    Column('permission_id', Integer, autoincrement=True, primary_key=True),
    Column('permission_name', Unicode(16), unique=True, nullable=False),
    Column('description', Unicode(255)),
    mysql_engine='InnoDB',
    mysql_charset='utf8',
)
categories = Table('categories', metadata,
    Column('id', Integer, autoincrement=True, primary_key=True),
    Column('name', Unicode(50), nullable=False, index=True),
    Column('slug', Unicode(slug_length), nullable=False, unique=True),
    Column('parent_id', Integer),
    ForeignKeyConstraint(['parent_id'], ['categories.id'],
        name='categories_ibfk_1',
        onupdate='CASCADE', ondelete='CASCADE'),
    mysql_engine='InnoDB',
    mysql_charset='utf8'
)
comments = Table('comments', metadata,
    Column('id', Integer, autoincrement=True, primary_key=True),
    Column('media_id', Integer),
    Column('subject', Unicode(100)),
    Column('created_on', DateTime, default=datetime.now, nullable=False),
    Column('modified_on', DateTime, default=datetime.now, onupdate=datetime.now, nullable=False),
    Column('reviewed', Boolean, default=False, nullable=False),
    Column('publishable', Boolean, default=False, nullable=False),
    Column('author_name', Unicode(50), nullable=False),
    Column('author_email', Unicode(255)),
    Column('author_ip', Integer, nullable=False),
    Column('body', UnicodeText, nullable=False),
    ForeignKeyConstraint(['media_id'], ['media.id'],
        name='comments_ibfk_1',
        onupdate='CASCADE', ondelete='CASCADE'),
    mysql_engine='InnoDB',
    mysql_charset='utf8',
)
media = Table('media', metadata,
    Column('id', Integer, autoincrement=True, primary_key=True),
    Column('type', Enum(VIDEO, AUDIO, name="type")),
    Column('slug', Unicode(slug_length), unique=True, nullable=False),
    Column('podcast_id', Integer),
    Column('reviewed', Boolean, default=False, nullable=False),
    Column('encoded', Boolean, default=False, nullable=False),
    Column('publishable', Boolean, default=False, nullable=False),

    Column('created_on', DateTime, default=datetime.now, nullable=False),
    Column('modified_on', DateTime, default=datetime.now, onupdate=datetime.now, nullable=False),
    Column('publish_on', DateTime),
    Column('publish_until', DateTime),

    Column('title', Unicode(255), nullable=False),
    Column('subtitle', Unicode(255)),
    Column('description', UnicodeText),
    Column('description_plain', UnicodeText),
    Column('notes', UnicodeText),

    Column('duration', Integer, default=0, nullable=False),
    Column('views', Integer, default=0, nullable=False),
    Column('likes', Integer, default=0, nullable=False),
    Column('popularity_points', Integer, default=0, nullable=False),

    Column('author_name', Unicode(50), nullable=False),
    Column('author_email', Unicode(255), nullable=False),

    ForeignKeyConstraint(['podcast_id'], ['podcasts.id'],
        name='media_ibfk_1',
        onupdate='CASCADE', ondelete='SET NULL'),

    mysql_engine='InnoDB',
    mysql_charset='utf8',
)
media_files = Table('media_files', metadata,
    Column('id', Integer, autoincrement=True, primary_key=True),
    Column('media_id', Integer, nullable=False),

    Column('type', Enum(VIDEO, AUDIO, AUDIO_DESC, CAPTIONS, name="type"), nullable=False),
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

    ForeignKeyConstraint(['media_id'], ['media.id'],
        name='media_files_ibfk_1',
        onupdate='CASCADE', ondelete='CASCADE'),

    mysql_engine='InnoDB',
    mysql_charset='utf8',
)
media_categories = Table('media_categories', metadata,
    Column('media_id', Integer, primary_key=True),
    Column('category_id', Integer, primary_key=True),
    ForeignKeyConstraint(['media_id'], ['media.id'],
        name='media_categories_ibfk_1',
        onupdate='CASCADE', ondelete='CASCADE'),
    ForeignKeyConstraint(['category_id'], ['categories.id'],
        name='media_categories_ibfk_2',
        onupdate='CASCADE', ondelete='CASCADE'),
    mysql_engine='InnoDB',
    mysql_charset='utf8',
)
media_tags = Table('media_tags', metadata,
    Column('media_id', Integer, primary_key=True),
    Column('tag_id', Integer, primary_key=True),
    ForeignKeyConstraint(['media_id'], ['media.id'],
        name='media_tags_ibfk_1',
        onupdate='CASCADE', ondelete='CASCADE'),
    ForeignKeyConstraint(['tag_id'], ['tags.id'],
        name='media_tags_ibfk_2',
        onupdate='CASCADE', ondelete='CASCADE'),
    mysql_engine='InnoDB',
    mysql_charset='utf8',
)
media_fulltext = Table('media_fulltext', metadata,
    Column('media_id', Integer, primary_key=True),
    Column('title', Unicode(255), nullable=False),
    Column('subtitle', Unicode(255)),
    Column('description_plain', UnicodeText),
    Column('notes', UnicodeText),
    Column('author_name', Unicode(50), nullable=False),
    Column('tags', UnicodeText),
    Column('categories', UnicodeText),
    mysql_engine='MyISAM',
    mysql_charset='utf8',
)
podcasts = Table('podcasts', metadata,
    Column('id', Integer, autoincrement=True, primary_key=True),
    Column('slug', Unicode(slug_length), unique=True, nullable=False),
    Column('created_on', DateTime, default=datetime.now, nullable=False),
    Column('modified_on', DateTime, default=datetime.now, onupdate=datetime.now, nullable=False),
    Column('title', Unicode(50), nullable=False),
    Column('subtitle', Unicode(255)),
    Column('description', UnicodeText),
    Column('category', Unicode(50)),
    Column('author_name', Unicode(50), nullable=False),
    Column('author_email', Unicode(50), nullable=False),
    Column('explicit', Boolean, default=None),
    Column('copyright', Unicode(50)),
    Column('itunes_url', Unicode(80)),
    Column('feedburner_url', Unicode(80)),
    mysql_engine='InnoDB',
    mysql_charset='utf8',
)
settings = Table('settings', metadata,
    Column('id', Integer, autoincrement=True, primary_key=True),
    Column('key', Unicode(255), nullable=False, unique=True),
    Column('value', UnicodeText),
    mysql_engine='InnoDB',
    mysql_charset='utf8',
)
tags = Table('tags', metadata,
    Column('id', Integer, autoincrement=True, primary_key=True),
    Column('name', Unicode(50), unique=True, nullable=False),
    Column('slug', Unicode(slug_length), unique=True, nullable=False),
    mysql_engine='InnoDB',
    mysql_charset='utf8'
)


def upgrade(migrate_engine):
    metadata.bind = migrate_engine
    connection = migrate_engine.connect()
    tables = metadata.sorted_tables

    # Drop all foreign key constraints so we can change the column type
    transaction = connection.begin()
    for table in tables:
        for constraint in table.constraints:
            if isinstance(constraint, ForeignKeyConstraint):
                if table is not comments:
                    constraint.drop()
                else:
                    # Ugh. the comments table created by the original setup.sql
                    # had an incorrectly named foreign key. Delete it manually.
                    subtrans = connection.begin_nested()
                    try:
                        constraint.drop()
                        subtrans.commit()
                    except OperationalError, e:
                        subtrans.rollback()
                        if 'comments_ibfk_1' in str(e):
                            connection.execute(
                                'ALTER TABLE %s '
                                'DROP FOREIGN KEY comments_media_fk1'
                            % table.name)
                        else:
                            raise
    transaction.commit()

    # Re-assign the integer type the SQLAlchemy way, which is not UNSIGNED
    transaction = connection.begin()
    for table in tables:
        for column in table.columns:
            if isinstance(column.type, Integer):
                if table is comments and column is comments.c.author_ip:
                    # Ugh. 32 bit IP addresses only fit when UNSIGNED is used, which postgres doesn't even support.
                    # Switching to a 64bit BIGINT for simplicity sake. IPv6 support will have to come later.
                    column.alter(type=BigInteger)
                else:
                    column.alter(type=Integer)
    transaction.commit()

    # Recreate our foreign key constraints
    transaction = connection.begin()
    for table in tables:
        for constraint in table.constraints:
            if isinstance(constraint, ForeignKeyConstraint):
                constraint.create()
    transaction.commit()

def downgrade(migrate_engine):
    raise NotImplementedError
