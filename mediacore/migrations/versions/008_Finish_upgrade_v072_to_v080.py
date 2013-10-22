# This file is a part of MediaDrop (http://www.mediadrop.net),
# Copyright 2009-2013 MediaCore Inc., Felix Schwarz and other contributors.
# For the exact contribution history, see the git revision log.
# The source code contained in this file is licensed under the GPLv3 or
# (at your option) any later version.
# See LICENSE.txt in the main project directory, for more information.

import os
from datetime import datetime
from urlparse import urlparse
from sqlalchemy import *
from migrate import *

from mediacore.lib.helpers import line_break_xhtml, strip_xhtml

metadata = MetaData()

media = Table('media', metadata,
    Column('id', Integer, autoincrement=True, primary_key=True),
    Column('type', String(10), nullable=False),
    Column('slug', String(50), unique=True, nullable=False),
    Column('podcast_id', Integer, ForeignKey('podcasts.id', onupdate='CASCADE', ondelete='CASCADE')),
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
)

media_files = Table('media_files', metadata,
    Column('id', Integer, autoincrement=True, primary_key=True),
    Column('media_id', Integer, ForeignKey('media.id', onupdate='CASCADE', ondelete='CASCADE'), nullable=False),

    Column('type', String(10), nullable=False),
    Column('container', String(10), nullable=False),
    Column('display_name', String(255), nullable=False),
    Column('file_name', String(255), nullable=False),
    Column('url', String(255), nullable=False),
    Column('embed', String(50), nullable=False),
    Column('size', Integer),

    Column('created_on', DateTime, default=datetime.now, nullable=False),
    Column('modified_on', DateTime, default=datetime.now, onupdate=datetime.now, nullable=False),
)

def upgrade(migrate_engine):
    metadata.bind = migrate_engine
    conn = migrate_engine.connect()
    transaction = conn.begin()
    try:
        generate_plain_descriptions(conn)
        update_media_file_types(conn)
        transaction.commit()
    except:
        transaction.rollback()
        raise

def generate_plain_descriptions(conn):
    values = []
    query = select([media.c.id, media.c.description, media.c.publish_on, media.c.likes])
    for media_id, desc, publish_on, likes in conn.execute(query):
        plain_desc = line_break_xhtml(desc)
        plain_desc = line_break_xhtml(plain_desc)
        plain_desc = strip_xhtml(plain_desc, True)
        popularity = calculate_popularity(publish_on, likes)
        values.append({
            'media_id': media_id,
            'desc': plain_desc,
            'popularity': popularity,
        })
    if values:
        query = media.update().where(media.c.id==bindparam('media_id'))\
                              .values(description_plain=bindparam('desc'),
                                      popularity_points=bindparam('popularity'))
        conn.execute(query, *values)

type_map = {
    'mp3': 'audio',
    'm4a': 'audio',
    'flac': 'audio',
}
embeddable_types = set(['youtube', 'vimeo', 'google'])

def update_media_file_types(conn):
    values = []
    query = select([media_files.c.id, media_files.c.container, media_files.c.url])
    for id, container, url in conn.execute(query):
        value = {
            'file_id': id,
            'type': type_map.get(container, 'video'),
            'display_name': None,
            'embed': None,
            'url': None,
        }
        urlp = urlparse(url)
        if container in embeddable_types:
            value['display_name'] = container.capitalize() + ' ID: ' + url
            value['embed'] = url
        elif urlp[1]:
            value['display_name'] = os.path.basename(url[2])
        else:
            value['display_name'] = value['file_name'] = url
        values.append(value)
    if values:
        query = media_files.update()\
            .where(media_files.c.id==bindparam('file_id'))\
            .values(type=bindparam('type'),
                    display_name=bindparam('display_name'),
                    embed=bindparam('embed'),
                    url=bindparam('url'))
        conn.execute(query, *values)

log_base = 4
base_life_hours = 36
now = datetime.now()
delta_start = datetime(2000, 1, 1)

def calculate_popularity(publish_on, likes):
    if publish_on is not None and publish_on < now:
        base_life = base_life_hours * 3600
        delta = publish_on - delta_start # since January 1, 2000
        t = delta.days * 86400 + delta.seconds
        popularity = math.log(likes, log_base) + t/base_life
        return max(int(popularity), 0)
    else:
        return 0

def downgrade(migrate_engine):
    pass
