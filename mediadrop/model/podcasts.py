# This file is a part of MediaDrop (http://www.mediadrop.net),
# Copyright 2009-2013 MediaDrop contributors
# For the exact contribution history, see the git revision log.
# The source code contained in this file is licensed under the GPLv3 or
# (at your option) any later version.
# See LICENSE.txt in the main project directory, for more information.

"""
Podcast Models

SQLAlchemy ORM definitions for:

* :class:`Podcast`

.. moduleauthor:: Nathan Wright <nathan@mediacore.com>

"""
from datetime import datetime
from sqlalchemy import Table, ForeignKey, Column, sql
from sqlalchemy.types import Unicode, UnicodeText, Integer, DateTime, Boolean, Float
from sqlalchemy.orm import mapper, relation, backref, synonym, composite, validates, dynamic_loader, column_property
from pylons import request

from mediadrop.model import Author, SLUG_LENGTH, slugify, get_available_slug
from mediadrop.model.meta import DBSession, metadata
from mediadrop.model.media import Media, MediaQuery, media
from mediadrop.plugin import events


podcasts = Table('podcasts', metadata,
    Column('id', Integer, autoincrement=True, primary_key=True, doc=\
        """The primary key ID."""),

    Column('slug', Unicode(SLUG_LENGTH), unique=True, nullable=False, doc=\
        """A unique URL-friendly permalink string for looking up this object.

        Be sure to call :func:`mediadrop.model.get_available_slug` to ensure
        the slug is unique."""),

    Column('created_on', DateTime, default=datetime.now, nullable=False, doc=\
        """The date and time this player was first created."""),

    Column('modified_on', DateTime, default=datetime.now, onupdate=datetime.now, nullable=False, doc=\
        """The date and time this player was last modified."""),

    Column('title', Unicode(50), nullable=False, doc=\
        """Display title."""),

    Column('subtitle', Unicode(255)),

    Column('description', UnicodeText),

    Column('category', Unicode(50), doc=\
        """The `iTunes category <http://www.apple.com/itunes/podcasts/specs.html#categories>`_

        Values with a ``>`` are parsed with special meaning. ``Arts > Design``
        implies that this pertains to the Design subcategory of Arts, and the
        feed markup reflects that."""),

    Column('author_name', Unicode(50), nullable=False),
    Column('author_email', Unicode(50), nullable=False),

    Column('explicit', Boolean, default=None, doc=\
        """The `iTunes explicit <http://www.apple.com/itunes/podcasts/specs.html#explicit>`_
        value.

            * ``True`` means 'yes'
            * ``None`` means no advisory displays, ie. 'no'
            * ``False`` means 'clean'

        """),

    Column('copyright', Unicode(50)),
    Column('itunes_url', Unicode(80), doc=\
        """Optional iTunes subscribe URL."""),

    Column('feedburner_url', Unicode(80), doc=\
        """Optional Feedburner URL.

        If set, requests for this podcast's feed will be forwarded to
        this address -- unless, of course, the request is coming from
        Feedburner."""),

    mysql_engine='InnoDB',
    mysql_charset='utf8',
)


class Podcast(object):
    """
    Podcast Metadata

    """
    query = DBSession.query_property()

    # TODO: replace '_thumb_dir' with something more generic, like 'name',
    #       so that its other uses throughout the code make more sense.
    _thumb_dir = 'podcasts'

    def __repr__(self):
        return '<Podcast: %r>' % self.slug

    @validates('slug')
    def validate_slug(self, key, slug):
        return slugify(slug)


mapper(Podcast, podcasts, order_by=podcasts.c.title, extension=events.MapperObserver(events.Podcast), properties={
    'author': composite(Author,
        podcasts.c.author_name,
        podcasts.c.author_email,
        doc="""An instance of :class:`mediadrop.model.authors.Author`.
               Although not actually a relation, it is implemented as if it were.
               This was decision was made to make it easier to integrate with
               :class:`mediadrop.model.auth.User` down the road."""),

    'media': dynamic_loader(Media, backref='podcast', query_class=MediaQuery, passive_deletes=True, doc=\
        """A query pre-filtered to media published under this podcast.
        Returns :class:`mediadrop.model.media.MediaQuery`."""),

    'media_count':
        column_property(
            sql.select(
                [sql.func.count(media.c.id)],
                media.c.podcast_id == podcasts.c.id,
            ).label('media_count'),
            deferred=True,
            doc="The total number of :class:`mediadrop.model.media.Media` episodes."
        ),
    'media_count_published':
        column_property(
            sql.select(
                [sql.func.count(media.c.id)],
                sql.and_(
                    media.c.podcast_id == podcasts.c.id,
                    media.c.reviewed == True,
                    media.c.encoded == True,
                    media.c.publishable == True,
                    media.c.publish_on <= sql.func.current_timestamp(),
                    sql.or_(
                        media.c.publish_until == None,
                        media.c.publish_until >= sql.func.current_timestamp(),
                    ),
                )
            ).label('media_count_published'),
            deferred=True,
            doc="The number of :class:`mediadrop.model.media.Media` episodes that are currently published."
        )
})
