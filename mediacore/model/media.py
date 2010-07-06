# This file is a part of MediaCore, Copyright 2009 Simple Station Inc.
#
# MediaCore is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# MediaCore is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
Media Models

SQLAlchemy ORM definitions for:

* :class:`Media`: metadata for a collection of one or more files.
* :class:`MediaFile`: a single audio or video file.

Additionally, :class:`Media` may be considered at podcast episode if it
belongs to a :class:`mediacore.model.podcasts.Podcast`.

.. moduleauthor:: Nathan Wright <nathan@simplestation.com>

"""

import math
import os.path
from datetime import datetime

from sqlalchemy import Table, ForeignKey, Column, sql, func
from sqlalchemy.types import String, Unicode, UnicodeText, Integer, DateTime, Boolean, Float, Enum
from sqlalchemy.orm import mapper, class_mapper, relation, backref, synonym, composite, column_property, comparable_property, dynamic_loader, validates, collections, attributes, Query
from sqlalchemy.schema import DDL
from pylons import app_globals, config, request

from mediacore.model import get_available_slug, slug_length, _mtm_count_property, _properties_dict_from_labels, MatchAgainstClause
from mediacore.model.meta import DBSession, metadata
from mediacore.model.authors import Author
from mediacore.model.comments import Comment, CommentQuery, comments
from mediacore.model.tags import Tag, TagList, tags, extract_tags, fetch_and_create_tags
from mediacore.model.categories import Category, CategoryList, categories
from mediacore.lib import helpers
from mediacore.lib.filetypes import AUDIO, AUDIO_DESC, CAPTIONS, VIDEO, guess_mimetype, pick_media_file_player
from mediacore.lib.embedtypes import external_embedded_containers

class MediaException(Exception): pass
class MediaFileException(MediaException): pass
class UnknownFileTypeException(MediaFileException): pass


media = Table('media', metadata,
    Column('id', Integer, autoincrement=True, primary_key=True),
    Column('type', Enum(VIDEO, AUDIO)),
    Column('slug', String(slug_length), unique=True, nullable=False),
    Column('podcast_id', Integer, ForeignKey('podcasts.id', onupdate='CASCADE', ondelete='SET NULL')),
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

    mysql_engine='InnoDB',
    mysql_charset='utf8',
)

media_files = Table('media_files', metadata,
    Column('id', Integer, autoincrement=True, primary_key=True),
    Column('media_id', Integer, ForeignKey('media.id', onupdate='CASCADE', ondelete='CASCADE'), nullable=False),

    Column('type', Enum(VIDEO, AUDIO, AUDIO_DESC, CAPTIONS), nullable=False),
    Column('container', String(10), nullable=False),
    Column('display_name', String(255), nullable=False),
    Column('file_name', String(255)),
    Column('url', String(255)),
    Column('embed', String(50)),
    Column('size', Integer),

    Column('created_on', DateTime, default=datetime.now, nullable=False),
    Column('modified_on', DateTime, default=datetime.now, onupdate=datetime.now, nullable=False),

    mysql_engine='InnoDB',
    mysql_charset='utf8',
)

media_tags = Table('media_tags', metadata,
    Column('media_id', Integer, ForeignKey('media.id', onupdate='CASCADE', ondelete='CASCADE'),
        primary_key=True),
    Column('tag_id', Integer, ForeignKey('tags.id', onupdate='CASCADE', ondelete='CASCADE'),
        primary_key=True),
    mysql_engine='InnoDB',
    mysql_charset='utf8',
)

media_categories = Table('media_categories', metadata,
    Column('media_id', Integer, ForeignKey('media.id', onupdate='CASCADE', ondelete='CASCADE'),
        primary_key=True),
    Column('category_id', Integer, ForeignKey('categories.id', onupdate='CASCADE', ondelete='CASCADE'),
        primary_key=True),
    mysql_engine='InnoDB',
    mysql_charset='utf8',
)

media_fulltext = Table('media_fulltext', metadata,
    Column('media_id', Integer, ForeignKey('media.id'), primary_key=True),
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

# Columns grouped by their FULLTEXT index
_fulltext_indexes = {
    'admin': (
        media_fulltext.c.title, media_fulltext.c.subtitle,
        media_fulltext.c.tags, media_fulltext.c.categories,
        media_fulltext.c.description_plain, media_fulltext.c.notes,
    ),
    'public': (
        media_fulltext.c.title, media_fulltext.c.subtitle,
        media_fulltext.c.tags, media_fulltext.c.categories,
        media_fulltext.c.description_plain,
    ),
}

def _setup_mysql_fulltext_indexes():
    for name, cols in _fulltext_indexes.iteritems():
        sql = (
            'ALTER TABLE %%(table)s '
            'ADD FULLTEXT INDEX media_fulltext_%(name)s (%(cols)s)'
        ) % {
            'name': name,
            'cols': ', '.join(col.name for col in cols)
        }
        DDL(sql, on='mysql').execute_at('after-create', media_fulltext)
_setup_mysql_fulltext_indexes()

class MediaQuery(Query):
    def reviewed(self, flag=True):
        return self.filter(Media.reviewed == flag)

    def encoded(self, flag=True):
        return self.filter(Media.encoded == flag)

    def published(self, flag=True):
        published = sql.and_(
            Media.reviewed == True,
            Media.encoded == True,
            Media.publishable == True,
            Media.publish_on <= datetime.now(),
            sql.or_(Media.publish_until == None,
                    Media.publish_until >= datetime.now()),
        )
        if flag:
            return self.filter(published)
        else:
            return self.filter(sql.not_(published))

    def order_by_status(self):
        return self.order_by(Media.reviewed.asc(),
                             Media.encoded.asc(),
                             Media.publishable.asc())

    def order_by_popularity(self):
        return self.order_by(Media.popularity_points.desc())

    def search(self, search, bool=False, order_by=True):
        search_cols = _fulltext_indexes['public']
        return self._search(search_cols, search, bool, order_by)

    def admin_search(self, search, bool=False, order_by=True):
        search_cols = _fulltext_indexes['admin']
        return self._search(search_cols, search, bool, order_by)

    def _search(self, search_cols, search, bool=False, order_by=True):
        if self.session.connection().dialect.name != 'mysql':
            # TODO: Use this fallback when triggers haven't been installed
            return self.filter(Media.title.like(search))
        filter = MatchAgainstClause(search_cols, search, bool)
        query = self.join(MediaFullText).filter(filter)
        if order_by:
            # MySQL automatically orders natural lang searches by relevance,
            # so override any existing ordering
            query = query.order_by(None)
            if bool:
                # To mimic the same behaviour in boolean mode, we must do an
                # extra natural language search on our boolean-filtered results
                relevance = MatchAgainstClause(search_cols, search, bool=False)
                query = query.order_by(relevance)
        return query

    def in_category(self, cat):
        all_cats = [cat]
        all_cats.extend(cat.descendants())
        all_ids = [c.id for c in all_cats]
        return self.filter(sql.exists(sql.select(
            [media_categories.c.media_id],
            sql.and_(media_categories.c.media_id == Media.id,
                     media_categories.c.category_id.in_(all_ids))
        )))

    def exclude(self, *args):
        """Exclude the given Media rows or IDs from the results.

        Accepts any number of arguments of Media instances, ids,
        lists of both, or None.
        """
        def _flatten(*args):
            ids = []
            for arg in args:
                if isinstance(arg, list):
                    ids.extend(_flatten(*arg))
                elif isinstance(arg, Media):
                    ids.append(int(arg.id))
                elif arg is not None:
                    ids.append(int(arg))
            return ids
        ids = _flatten(*args)
        if ids:
            return self.filter(sql.not_(Media.id.in_(ids)))
        else:
            return self

class Media(object):
    """
    Media metadata and a collection of related files.

    **Primary Data**

    .. attribute:: id

    .. attribute:: slug

        A unique URL-friendly permalink string for looking up this object.
        Be sure to call :func:`mediacore.model.get_available_slug` to ensure
        the slug is unique.

    .. attribute:: type

        Indicates whether the media is to be considered audio or video.

        If this object has no files, the type is None.
        See :meth:`Media.update_type` for details on how this is determined.

    .. attribute:: reviewed

        A flag to indicate whether this file has passed review by an admin.

    .. attribute:: encoded

        A flag to indicate whether this file is encoded in a web-ready state.

    .. attribute:: publishable

        A flag to indicate if this media should be published in between its
        publish_on and publish_until dates. If this is false, this is
        considered to be in draft state and will not appear on the site.

    .. attribute:: created_on
    .. attribute:: modified_on

    .. attribute:: publish_on
    .. attribute:: publish_until

        A datetime range during which this object should be published.
        The range may be open ended by leaving ``publish_until`` empty.

    .. attribute:: title

        Display title

    .. attribute:: subtitle

        An optional subtitle intended mostly for podcast episodes.
        If none is provided, the title is concatenated and used in its place.

    .. attribute:: description

        A public-facing XHTML description. Should be a paragraph or more.

    .. attribute:: description_plain

        A public-facing plaintext description. Should be a paragraph or more.

    .. attribute:: duration

        Play time in seconds

    .. attribute:: views

        The number of times the public media page has been viewed

    .. attribute:: likes

        The number of users who clicked 'i like this'.

    .. attribute:: notes

        Notes for administrative use -- never displayed publicly.

    .. attribute:: author

        An instance of :class:`mediacore.model.authors.Author`.
        Although not actually a relation, it is implemented as if it were.
        This was decision was made to make it easier to integrate with
        :class:`mediacore.model.auth.User` down the road.

    **Relations**

    .. attribute:: podcast_id
    .. attribute:: podcast

        An optional :class:`mediacore.model.podcasts.Podcast` to publish this object in.

    .. attribute:: files

        A list of :class:`MediaFile` instances.

    .. attribute:: categories

        A list of :class:`mediacore.model.categories.Category`.

        See the :meth:`set_categories` helper.

    .. attribute:: tags

        A list of :class:`mediacore.model.tags.Tag`.

        See the :meth:`set_tags` helper.

    .. attribute:: comments

        A dynamic loader for related comments,
        see :class:`mediacore.model.comments.CommentQuery`.

        .. todo:: Reimplement as a dynamic loader.

    .. attribute:: comment_count
    .. attribute:: comment_count_published

    """

    query = DBSession.query_property(MediaQuery)

    _thumb_dir = 'media'

    def __init__(self):
        if self.author is None:
            self.author = Author()

    def __repr__(self):
        return '<Media: %s>' % self.slug

    def set_tags(self, tags):
        """Set the tags relations of this media, creating them as needed.

        :param tags: A list or comma separated string of tags to use.
        """
        if isinstance(tags, basestring):
            tags = extract_tags(tags)
        if isinstance(tags, list) and tags:
            tags = fetch_and_create_tags(tags)
        self.tags = tags or []

    def set_categories(self, cats):
        """Set the related categories of this media.

        :param cats: A list of category IDs to set.
        """
        if cats:
            cats = Category.query.filter(Category.id.in_(cats)).all()
        self.categories = cats or []

    def update_status(self):
        """Ensure the type (audio/video) and encoded flag are properly set.

        Call this after modifying any files belonging to this item.

        """
        self.type = self._update_type()
        self.encoded = self._update_encoding()

    def _update_type(self):
        """Update the type of this Media object.

        If there's a video file, mark this as a video type, else fallback
        to audio, if possible, or unknown (None)
        """
        if any(file.type == VIDEO for file in self.files):
            return VIDEO
        elif any(file.type == AUDIO for file in self.files):
            return AUDIO
        else:
            return None

    def _update_encoding(self):
        # Test to see if we can find a workable file/player conbination
        # for the most common podcasting app w/ the POOREST format support
        if self.podcast_id \
        and not helpers.pick_podcast_media_file(self.files):
            return False
        # Test to see if we can find a workable file/player conbination
        # for the browser w/ the BEST format support
        if not helpers.pick_any_media_file(self.files):
            return False
        return True

    @property
    def downloadable_file(self):
        if not self.files or not self.type:
            return None
        primaries = [file for file in self.files if file.type == self.type]
        primaries.sort(key=lambda file: file.size)
        if not primaries or primaries[-1].embed:
            return None
        return primaries[-1]

    @property
    def captions(self):
        for file in self.files:
            if file.type == CAPTIONS:
                return file
        return None

    @property
    def audio_desc(self):
        for file in self.files:
            if file.type == AUDIO_DESC:
                return file
        return None

    @property
    def is_published(self):
        if self.id is None:
            return False
        return self.publishable and self.reviewed and self.encoded\
           and (self.publish_on is not None and self.publish_on <= datetime.now())\
           and (self.publish_until is None or self.publish_until >= datetime.now())

    def increment_views(self):
        """Increment the number of views in the database.

        We avoid concurrency issues by incrementing JUST the views and
        not allowing modified_on to be updated automatically.

        """
        if self.id is None:
            self.views += 1
            return self.views

        query = 'UPDATE %s SET %s = (%s + 1) WHERE %s = :media_id' \
              % (media, media.c.views, media.c.views, media.c.id)
        DBSession.execute(query, {'media_id': self.id})

        # Increment the views by one for the rest of the request,
        # but don't allow the ORM to increment the views too.
        attributes.set_committed_value(self, 'views', self.views + 1)
        return self.views

    def increment_likes(self):
        self.update_popularity()
        # update the number of likes with an expression, to avoid concurrency
        # issues associated with simultaneous writes.
        likes = self.likes + 1
        self.likes = media.c.likes + sql.text('1')
        return likes

    def update_popularity(self):
        # FIXME: The current algorithm assumes that the earliest publication
        #        date is January 1, 2000.

        # In our ranking algorithm, being base_life_hours newer is equivalent
        # to having log_base times more votes.
        log_base = int(app_globals.settings['popularity_decay_exponent'])
        base_life_hours = int(app_globals.settings['popularity_decay_lifetime'])

        if self.is_published:
            base_life = base_life_hours * 3600
            delta = self.publish_on - datetime(2000, 1, 1) # since January 1, 2000
            t = delta.days * 86400 + delta.seconds
            popularity = math.log(self.likes+1, log_base) + t/base_life
            self.popularity_points = max(int(popularity), 0)
        else:
            self.popularity_points = 0

    @validates('description')
    def _validate_description(self, key, value):
        self.description_plain = helpers.line_break_xhtml(
            helpers.line_break_xhtml(value)
        )
        return value

    @validates('description_plain')
    def _validate_description_plain(self, key, value):
        return helpers.strip_xhtml(value, True)

class MediaFile(object):
    """
    Audio or Video file or link

    Represents a locally- or remotely- hosted file or an embeddable YouTube video.

    """
    query = DBSession.query_property()

    def __repr__(self):
        return '<MediaFile: %s %s url=%s>' % (self.type, self.container, self.url)

    @property
    def mimetype(self):
        """The best-guess mimetype based on this file's container format.

        Defaults to 'application/octet-stream'.
        """
        type = self.type
        if type == AUDIO_DESC:
            type = AUDIO
        return guess_mimetype(self.container, type)

    @property
    def file_path(self):
        if self.file_name:
            return os.path.join(config['media_dir'], self.file_name)
        return None

    def play_url(self, qualified=False):
        """The URL for use when embedding the media file in a page

        This MAY return a different URL than the link_url property.
        """
        if self.url is not None:
            return self.url
        elif self.embed is not None:
            return external_embedded_containers[self.container]['play'] % self.embed
        else:
            return helpers.url_for(controller='/media', action='serve',
                                   slug=self.media.slug, id=self.id,
                                   container=self.container, qualified=qualified)

    def link_url(self, qualified=False):
        """The URL for use when linking to a media file.

        This is usually a direct link to the file, but for youtube videos and
        other files marked as embeddable, this may return a link to the hosting
        site's view page.

        This MAY return a different URL than the play_url property.
        """
        if self.url is not None:
            return self.url
        elif self.embed is not None:
            return external_embedded_containers[self.container]['link'] % self.embed
        else:
            return helpers.url_for(controller='/media', action='serve',
                                   slug=self.media.slug, id=self.id,
                                   container=self.container, qualified=qualified)

class MediaFullText(object):
    query = DBSession.query_property()


mapper(MediaFile, media_files)

mapper(MediaFullText, media_fulltext)

_media_mapper = mapper(Media, media, order_by=media.c.title, properties={
    'fulltext': relation(MediaFullText, uselist=False, passive_deletes=True),
    'author': composite(Author, media.c.author_name, media.c.author_email),
    'files': relation(MediaFile, backref='media', order_by=media_files.c.type.asc(), passive_deletes=True),
    'tags': relation(Tag, secondary=media_tags, backref=backref('media', lazy='dynamic', query_class=MediaQuery), collection_class=TagList, passive_deletes=True),
    'categories': relation(Category, secondary=media_categories, backref=backref('media', lazy='dynamic', query_class=MediaQuery), collection_class=CategoryList, passive_deletes=True),

    'comments': dynamic_loader(Comment, backref='media', query_class=CommentQuery, passive_deletes=True),
    'comment_count': column_property(
        sql.select([sql.func.count(comments.c.id)],
                   media.c.id == comments.c.media_id).label('comment_count'),
        deferred=True),
    'comment_count_published': column_property(
        sql.select([sql.func.count(comments.c.id)],
                   sql.and_(comments.c.media_id == media.c.id,
                            comments.c.publishable == True)).label('comment_count_published'),
        deferred=True),
})

# Add properties for counting how many media items have a given Tag
_tags_mapper = class_mapper(Tag, compile=False)
_tags_mapper.add_properties(_properties_dict_from_labels(
    _mtm_count_property('media_count', media_tags),
    _mtm_count_property('media_count_published', media_tags, [
        media.c.reviewed == True,
        media.c.encoded == True,
        media.c.publishable == True,
        media.c.publish_on <= datetime.now(),
        sql.or_(media.c.publish_until == None,
                media.c.publish_until >= datetime.now()),
    ]),
))

# Add properties for counting how many media items have a given Category
_categories_mapper = class_mapper(Category, compile=False)
_categories_mapper.add_properties(_properties_dict_from_labels(
    _mtm_count_property('media_count', media_categories),
    _mtm_count_property('media_count_published', media_categories, [
        media.c.reviewed == True,
        media.c.encoded == True,
        media.c.publishable == True,
        media.c.publish_on <= datetime.now(),
        sql.or_(media.c.publish_until == None,
                media.c.publish_until >= datetime.now()),
    ]),
))
