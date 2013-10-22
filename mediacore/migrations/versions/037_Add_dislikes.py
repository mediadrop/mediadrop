# This file is a part of MediaDrop (http://www.mediadrop.net),
# Copyright 2009-2013 MediaCore Inc., Felix Schwarz and other contributors.
# For the exact contribution history, see the git revision log.
# The source code contained in this file is licensed under the GPLv3 or
# (at your option) any later version.
# See LICENSE.txt in the main project directory, for more information.

import logging
from datetime import datetime

from sqlalchemy import *
from migrate import *

log = logging.getLogger(__name__)

SLUG_LENGTH = 50

metadata = MetaData()
media = Table('media', metadata,
    Column('id', Integer, autoincrement=True, primary_key=True, doc=\
        """The primary key ID."""),

    Column('type', Unicode(8), doc=\
        """Indicates whether the media is to be considered audio or video.

        If this object has no files, the type is None.
        See :meth:`Media.update_type` for details on how this is determined."""),

    Column('slug', Unicode(SLUG_LENGTH), unique=True, nullable=False, doc=\
        """A unique URL-friendly permalink string for looking up this object.

        Be sure to call :func:`mediacore.model.get_available_slug` to ensure
        the slug is unique."""),

    Column('podcast_id', Integer, ForeignKey('podcasts.id', onupdate='CASCADE', ondelete='SET NULL'), doc=\
        """The primary key of a podcast to publish this media under."""),

    Column('reviewed', Boolean, default=False, nullable=False, doc=\
        """A flag to indicate whether this file has passed review by an admin."""),

    Column('encoded', Boolean, default=False, nullable=False, doc=\
        """A flag to indicate whether this file is encoded in a web-ready state."""),

    Column('publishable', Boolean, default=False, nullable=False, doc=\
        """A flag to indicate if this media should be published in between its
        publish_on and publish_until dates. If this is false, this is
        considered to be in draft state and will not appear on the site."""),

    Column('created_on', DateTime, default=datetime.now, nullable=False, doc=\
        """The date and time this player was first created."""),

    Column('modified_on', DateTime, default=datetime.now, onupdate=datetime.now, nullable=False, doc=\
        """The date and time this player was last modified."""),

    Column('publish_on', DateTime, doc=\
        """A datetime range during which this object should be published.
        The range may be open ended by leaving ``publish_until`` empty."""),

    Column('publish_until', DateTime, doc=\
        """A datetime range during which this object should be published.
        The range may be open ended by leaving ``publish_until`` empty."""),

    Column('title', Unicode(255), nullable=False, doc=\
        """Display title."""),

    Column('subtitle', Unicode(255), doc=\
        """An optional subtitle intended mostly for podcast episodes.
        If none is provided, the title is concatenated and used in its place."""),

    Column('description', UnicodeText, doc=\
        """A public-facing XHTML description. Should be a paragraph or more."""),

    Column('description_plain', UnicodeText, doc=\
        """A public-facing plaintext description. Should be a paragraph or more."""),

    Column('notes', UnicodeText, doc=\
        """Notes for administrative use -- never displayed publicly."""),

    Column('duration', Integer, default=0, nullable=False, doc=\
        """Play time in seconds."""),

    Column('views', Integer, default=0, nullable=False, doc=\
        """The number of times the public media page has been viewed."""),

    Column('likes', Integer, default=0, nullable=False, doc=\
        """The number of users who clicked 'i like this'."""),

    Column('dislikes', Integer, default=0, nullable=False, doc=\
        """The number of users who clicked 'i DONT like this'."""),

    Column('popularity_points', Integer, default=0, nullable=False, doc=\
        """An integer score of how 'hot' this media is.

        Newer items with some likes are favoured over older items with
        more likes. In other words, ordering on this column will always
        bring the newest most liked items to the top. `More info
        <http://amix.dk/blog/post/19588>`_."""),

    Column('popularity_likes', Integer, default=0, nullable=False, doc=\
        """An integer score of how 'hot' liking this media is.

        Newer items with some likes are favoured over older items with
        more likes. In other words, ordering on this column will always
        bring the newest most liked items to the top. `More info
        <http://amix.dk/blog/post/19588>`_."""),

    Column('popularity_dislikes', Integer, default=0, nullable=False, doc=\
        """An integer score of how 'hot' unliking this media is.

        Newer items with some likes are favoured over older items with
        more likes. In other words, ordering on this column will always
        bring the newest most liked items to the top. `More info
        <http://amix.dk/blog/post/19588>`_."""),

    Column('author_name', Unicode(50), nullable=False),
    Column('author_email', Unicode(255), nullable=False),

    mysql_engine='InnoDB',
    mysql_charset='utf8',
)

def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind migrate_engine
    # to your metadata
    metadata.bind = migrate_engine
    conn = migrate_engine.connect()

    transaction = conn.begin()
    media.c.dislikes.create(media)
    media.c.popularity_likes.create(media)
    media.c.popularity_dislikes.create(media)
    transaction.commit()

    transaction = conn.begin()
    query = select([
        media.c.id,
        media.c.popularity_points,
    ])
    for media_id, popularity_points in conn.execute(query):
        conn.execute(media.update(media.c.id == media_id, {
            'popularity_likes': popularity_points,
        }))
    transaction.commit()

def downgrade(migrate_engine):
    raise NotImplementedError()
