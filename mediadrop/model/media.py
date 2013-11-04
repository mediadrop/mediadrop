# This file is a part of MediaDrop (http://www.mediadrop.net),
# Copyright 2009-2013 MediaDrop contributors
# For the exact contribution history, see the git revision log.
# The source code contained in this file is licensed under the GPLv3 or
# (at your option) any later version.
# See LICENSE.txt in the main project directory, for more information.

"""
Media Models

SQLAlchemy ORM definitions for:

* :class:`Media`: metadata for a collection of one or more files.
* :class:`MediaFile`: a single audio or video file.

Additionally, :class:`Media` may be considered at podcast episode if it
belongs to a :class:`mediadrop.model.podcasts.Podcast`.

.. moduleauthor:: Nathan Wright <nathan@mediacore.com>

"""

from datetime import datetime

from sqlalchemy import Table, ForeignKey, Column, event, sql
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import (attributes, backref, class_mapper, column_property,
    composite, dynamic_loader, mapper, Query, relation, validates)
from sqlalchemy.orm.collections import attribute_mapped_collection
from sqlalchemy.schema import DDL
from sqlalchemy.types import Boolean, DateTime, Integer, Unicode, UnicodeText

from mediadrop.lib.auth import Resource
from mediadrop.lib.compat import any
from mediadrop.lib.filetypes import AUDIO, AUDIO_DESC, VIDEO, guess_mimetype
from mediadrop.lib.players import pick_any_media_file, pick_podcast_media_file
from mediadrop.lib.util import calculate_popularity
from mediadrop.lib.xhtml import line_break_xhtml, strip_xhtml
from mediadrop.model import (get_available_slug, SLUG_LENGTH, 
    _mtm_count_property, _properties_dict_from_labels, MatchAgainstClause)
from mediadrop.model.meta import DBSession, metadata
from mediadrop.model.authors import Author
from mediadrop.model.categories import Category, CategoryList
from mediadrop.model.comments import Comment, CommentQuery, comments
from mediadrop.model.tags import Tag, TagList, extract_tags, fetch_and_create_tags
from mediadrop.plugin import events


media = Table('media', metadata,
    Column('id', Integer, autoincrement=True, primary_key=True, doc=\
        """The primary key ID."""),

    Column('type', Unicode(8), doc=\
        """Indicates whether the media is to be considered audio or video.

        If this object has no files, the type is None.
        See :meth:`Media.update_type` for details on how this is determined."""),

    Column('slug', Unicode(SLUG_LENGTH), unique=True, nullable=False, doc=\
        """A unique URL-friendly permalink string for looking up this object.

        Be sure to call :func:`mediadrop.model.get_available_slug` to ensure
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
        """An integer score of how 'hot' (likes - dislikes) this media is.

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
        """An integer score of how 'hot' disliking this media is.

        Newer items with some likes are favoured over older items with
        more likes. In other words, ordering on this column will always
        bring the newest most liked items to the top. `More info
        <http://amix.dk/blog/post/19588>`_."""),

    Column('author_name', Unicode(50), nullable=False),
    Column('author_email', Unicode(255), nullable=False),

    mysql_engine='InnoDB',
    mysql_charset='utf8',
)

media_meta = Table('media_meta', metadata,
    Column('id', Integer, autoincrement=True, primary_key=True),
    Column('media_id', Integer, ForeignKey('media.id', onupdate='CASCADE', ondelete='CASCADE'), nullable=False),
    Column('key', Unicode(64), nullable=False),
    Column('value', UnicodeText, default=None),

    mysql_engine='InnoDB',
    mysql_charset='utf8',
)

media_files = Table('media_files', metadata,
    Column('id', Integer, autoincrement=True, primary_key=True),
    Column('media_id', Integer, ForeignKey('media.id', onupdate='CASCADE', ondelete='CASCADE'), nullable=False),
    Column('storage_id', Integer, ForeignKey('storage.id', onupdate='CASCADE', ondelete='CASCADE'), nullable=False),

    Column('type', Unicode(16), nullable=False),
    Column('container', Unicode(10)),
    Column('display_name', Unicode(255), nullable=False),
    Column('unique_id', Unicode(255)),
    Column('size', Integer),

    Column('created_on', DateTime, default=datetime.now, nullable=False),
    Column('modified_on', DateTime, default=datetime.now, onupdate=datetime.now, nullable=False),

    Column('bitrate', Integer),
    Column('width', Integer),
    Column('height', Integer),

    mysql_engine='InnoDB',
    mysql_charset='utf8',
)

media_files_meta = Table('media_files_meta', metadata,
    Column('id', Integer, autoincrement=True, primary_key=True),
    Column('media_files_id', Integer, ForeignKey('media_files.id', onupdate='CASCADE', ondelete='CASCADE'), nullable=False),
    Column('key', Unicode(64), nullable=False),
    Column('value', UnicodeText, default=None),

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
        event.listen(
            media_fulltext,
            u'after_create',
            DDL(sql).execute_if(dialect=u'mysql')
        )
_setup_mysql_fulltext_indexes()

class MediaQuery(Query):
    def reviewed(self, flag=True):
        return self.filter(Media.reviewed == flag)

    def encoded(self, flag=True):
        return self.filter(Media.encoded == flag)

    def drafts(self, flag=True):
        drafts = sql.and_(
            Media.publishable == False,
            Media.reviewed == True,
            Media.encoded == True,
        )
        if flag:
            return self.filter(drafts)
        else:
            return self.filter(sql.not_(drafts))

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
        # XXX: If full text searching is not enabled, we use a very
        #      rudimentary fallback.
        if not self._fulltext_enabled():
            return self.filter(sql.or_(Media.title.ilike("%%%s%%" % search),
                                       Media.description_plain.ilike("%%%s%%" % search)))

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

    def _fulltext_enabled(self):
        connection = self.session.connection()
        if connection.dialect.name == 'mysql':
            # use a fun trick to see if the media_fulltext table is being used
            # thanks to this guy: http://data.agaric.com/node/2241#comment-544
            select = sql.select('1').select_from(media_fulltext).limit(1)
            result = connection.execute(select)
            if result.scalar() is not None:
                return True
        return False

    def in_category(self, cat):
        """Filter results to Media in the given category"""
        return self.in_categories([cat])

    def in_categories(self, cats):
        """Filter results to Media in at least one of the given categories"""
        if len(cats) == 0:
            # SQLAlchemy complains about an empty IN-predicate
            return self.filter(media_categories.c.media_id == -1)
        all_cats = cats[:]
        for cat in cats:
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

    def related(self, media):
        query = self.published().filter(Media.id != media.id)

        # XXX: If full text searching is not enabled, we simply return media
        #      in the same categories.
        if not self._fulltext_enabled():
            return query.in_categories(media.categories)

        search_terms = '%s %s %s' % (
            media.title,
            media.fulltext and media.fulltext.tags or '',
            media.fulltext and media.fulltext.categories or '',
        )
        return query.search(search_terms, bool=True)

class Meta(object):
    """
    Metadata related to a media object

    .. attribute:: id

    .. attribute:: key

        A lookup key

    .. attribute:: value

        The metadata value

    """
    def __init__(self, key, value):
        self.key = key
        self.value = value

class MediaMeta(Meta):
    pass

class MediaFilesMeta(Meta):
    pass

class Media(object):
    """
    Media metadata and a collection of related files.

    """
    meta = association_proxy('_meta', 'value', creator=MediaMeta)

    query = DBSession.query_property(MediaQuery)

    # TODO: replace '_thumb_dir' with something more generic, like 'name',
    #       so that its other uses throughout the code make more sense.
    _thumb_dir = 'media'

    def __init__(self):
        if self.author is None:
            self.author = Author()

    def __repr__(self):
        return '<Media: %r>' % self.slug

    @classmethod
    def example(cls, **kwargs):
        media = Media()
        defaults = dict(
            title=u'Foo Media',
            author=Author(u'Joe', u'joe@site.example'),
            
            type = None,
        )
        defaults.update(kwargs)
        defaults.setdefault('slug', get_available_slug(Media, defaults['title']))
        for key, value in defaults.items():
            assert hasattr(media, key)
            setattr(media, key, value)
        DBSession.add(media)
        DBSession.flush()
        return media

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
        was_encoded = self.encoded
        self.type = self._update_type()
        self.encoded = self._update_encoding()
        if self.encoded and not was_encoded:
            events.Media.encoding_done(self)

    def _update_type(self):
        """Update the type of this Media object.

        If there's a video file, mark this as a video type, else fallback
        to audio, if possible, or unknown (None)
        """
        if any(file.type == VIDEO for file in self.files):
            return VIDEO
        elif any(file.type == AUDIO for file in self.files):
            return AUDIO
        return None

    def _update_encoding(self):
        # Test to see if we can find a workable file/player combination
        # for the most common podcasting app w/ the POOREST format support
        if self.podcast_id and not pick_podcast_media_file(self):
            return False
        # Test to see if we can find a workable file/player combination
        # for the browser w/ the BEST format support
        if not pick_any_media_file(self):
            return False
        return True

    @property
    def is_published(self):
        if self.id is None:
            return False
        return self.publishable and self.reviewed and self.encoded\
           and (self.publish_on is not None and self.publish_on <= datetime.now())\
           and (self.publish_until is None or self.publish_until >= datetime.now())

    @property
    def resource(self):
        return Resource('media', self.id, media=self)

    def increment_views(self):
        """Increment the number of views in the database.

        We avoid concurrency issues by incrementing JUST the views and
        not allowing modified_on to be updated automatically.

        """
        if self.id is None:
            self.views += 1
            return self.views

        DBSession.execute(media.update()\
            .values(views=media.c.views + 1)\
            .where(media.c.id == self.id))

        # Increment the views by one for the rest of the request,
        # but don't allow the ORM to increment the views too.
        attributes.set_committed_value(self, 'views', self.views + 1)
        return self.views

    def increment_likes(self):
        self.likes += 1
        self.update_popularity()
        return self.likes

    def increment_dislikes(self):
        self.dislikes += 1
        self.update_popularity()
        return self.dislikes

    def update_popularity(self):
        if self.is_published:
            self.popularity_points = calculate_popularity(
                self.publish_on,
                self.likes - self.dislikes,
            )
            self.popularity_likes = calculate_popularity(
                self.publish_on,
                self.likes,
            )
            self.popularity_dislikes = calculate_popularity(
                self.publish_on,
                self.dislikes,
            )
        else:
            self.popularity_points = 0
            self.popularity_likes = 0
            self.popularity_dislikes = 0

    @validates('description')
    def _validate_description(self, key, value):
        self.description_plain = line_break_xhtml(
            line_break_xhtml(value)
        )
        return value

    @validates('description_plain')
    def _validate_description_plain(self, key, value):
        return strip_xhtml(value, True)

    def get_uris(self):
        uris = []
        for file in self.files:
            uris.extend(file.get_uris())
        return uris

class MediaFileQuery(Query):
    pass

class MediaFile(object):
    """
    Audio or Video File

    """
    meta = association_proxy('_meta', 'value', creator=MediaFilesMeta)
    query = DBSession.query_property(MediaFileQuery)

    def __repr__(self):
        return '<MediaFile: %r %r unique_id=%r>' \
            % (self.type, self.storage.display_name, self.unique_id)

    @property
    def mimetype(self):
        """The best-guess mimetype based on this file's container format.

        Defaults to 'application/octet-stream'.
        """
        type = self.type
        if type == AUDIO_DESC:
            type = AUDIO
        return guess_mimetype(self.container, type)

    def get_uris(self):
        """Return a list all possible playback URIs for this file.

        :rtype: list
        :returns: :class:`mediadrop.lib.storage.StorageURI` instances.

        """
        return self.storage.get_uris(self)

class MediaFullText(object):
    query = DBSession.query_property()

mapper(MediaFullText, media_fulltext)
mapper(MediaMeta, media_meta)
mapper(MediaFilesMeta, media_files_meta)

_media_files_mapper = mapper(
    MediaFile, media_files,
    extension=events.MapperObserver(events.MediaFile),
    properties={
        '_meta': relation(
            MediaFilesMeta,
            collection_class=attribute_mapped_collection('key'),
            passive_deletes=True,
        ),
    },
)

_media_mapper = mapper(
    Media, media,
    order_by=media.c.title,
    extension=events.MapperObserver(events.Media),
    properties={
        'fulltext': relation(
            MediaFullText,
            uselist=False,
            passive_deletes=True,
        ),
        'author': composite(
            Author,
            media.c.author_name,
            media.c.author_email,
            doc="""An instance of :class:`mediadrop.model.authors.Author`.
                   Although not actually a relation, it is implemented as if it were.
                   This was decision was made to make it easier to integrate with
                   :class:`mediadrop.model.auth.User` down the road."""
        ),
        'files': relation(
            MediaFile,
            backref='media',
            order_by=media_files.c.type.asc(),
            passive_deletes=True,
            doc="""A list of :class:`MediaFile` instances."""
        ),
        'tags': relation(
            Tag,
            secondary=media_tags,
            backref=backref('media', lazy='dynamic', query_class=MediaQuery),
            collection_class=TagList,
            passive_deletes=True,
            doc="""A list of :class:`mediadrop.model.tags.Tag`."""
        ),
        'categories': relation(
            Category,
            secondary=media_categories,
            backref=backref('media', lazy='dynamic', query_class=MediaQuery),
            collection_class=CategoryList,
            passive_deletes=True,
            doc="""A list of :class:`mediadrop.model.categories.Category`."""
        ),
        '_meta': relation(
            MediaMeta,
            collection_class=attribute_mapped_collection('key'),
            passive_deletes=True,
        ),
        'comments': dynamic_loader(
            Comment,
            backref='media',
            query_class=CommentQuery,
            passive_deletes=True,
            doc="""A query pre-filtered for associated comments.
                   Returns :class:`mediadrop.model.comments.CommentQuery`."""
        ),
        'comment_count': column_property(
            sql.select(
                [sql.func.count(comments.c.id)],
                media.c.id == comments.c.media_id,
            ).label('comment_count'),
            deferred=True,
        ),
        'comment_count_published': column_property(
            sql.select(
                [sql.func.count(comments.c.id)],
                sql.and_(
                    comments.c.media_id == media.c.id,
                    comments.c.publishable == True,
                )
            ).label('comment_count_published'),
            deferred=True,
        ),
})

# Add properties for counting how many media items have a given Tag
_tags_mapper = class_mapper(Tag, compile=False)
_tags_mapper.add_properties(_properties_dict_from_labels(
    _mtm_count_property('media_count', media_tags),
    _mtm_count_property('media_count_published', media_tags, [
        media.c.reviewed == True,
        media.c.encoded == True,
        media.c.publishable == True,
        media.c.publish_on <= sql.func.current_timestamp(),
        sql.or_(
            media.c.publish_until == None,
            media.c.publish_until >= sql.func.current_timestamp(),
        ),
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
        media.c.publish_on <= sql.func.current_timestamp(),
        sql.or_(
            media.c.publish_until == None,
            media.c.publish_until >= sql.func.current_timestamp(),
        ),
    ]),
))
