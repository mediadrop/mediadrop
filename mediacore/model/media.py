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
import transaction
from datetime import datetime
from urlparse import urlparse
from sqlalchemy import Table, ForeignKey, Column, sql, func
from sqlalchemy.types import String, Unicode, UnicodeText, Integer, DateTime, Boolean, Float
from sqlalchemy.orm import mapper, class_mapper, relation, backref, synonym, composite, column_property, comparable_property, dynamic_loader, validates, collections, Query
from tg import config, request
from zope.sqlalchemy import datamanager

from mediacore.model import metadata, DBSession, get_available_slug, _mtm_count_property, _properties_dict_from_labels, _MatchAgainstClause
from mediacore.model.authors import Author
from mediacore.model.comments import Comment, CommentQuery, comments
from mediacore.model.settings import fetch_setting
from mediacore.model.tags import Tag, TagList, tags, extract_tags, fetch_and_create_tags
from mediacore.model.topics import Topic, TopicList, topics, fetch_topics
from mediacore.lib import helpers

class MediaException(Exception): pass
class MediaFileException(MediaException): pass
class UnknownFileTypeException(MediaFileException): pass


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
    Column('url', String(255), nullable=False),

    Column('size', Integer),
    Column('width', Integer),
    Column('height', Integer),
    Column('bitrate', Integer),

    Column('enable_player', Boolean, default=True, nullable=False),
    Column('enable_feed', Boolean, default=True, nullable=False),

    Column('created_on', DateTime, default=datetime.now, nullable=False),
    Column('modified_on', DateTime, default=datetime.now, onupdate=datetime.now, nullable=False),
)
media_files.append_column(
    # The position defaults to the greatest file position for this media plus 1.
    Column('position', Integer, nullable=False, default=sql.select(
        [func.coalesce(func.max(sql.text('mf.position + 1')), sql.text('1'))],
        sql.text('mf.media_id') == sql.bindparam('media_id'),
        media_files.alias('mf')
    ))
)

media_tags = Table('media_tags', metadata,
    Column('media_id', Integer, ForeignKey('media.id', onupdate='CASCADE', ondelete='CASCADE'),
        primary_key=True),
    Column('tag_id', Integer, ForeignKey('tags.id', onupdate='CASCADE', ondelete='CASCADE'),
        primary_key=True)
)

media_topics = Table('media_topics', metadata,
    Column('media_id', Integer, ForeignKey('media.id', onupdate='CASCADE', ondelete='CASCADE'),
        primary_key=True),
    Column('topic_id', Integer, ForeignKey('topics.id', onupdate='CASCADE', ondelete='CASCADE'),
        primary_key=True)
)

media_fulltext = Table('media_fulltext', metadata,
    Column('media_id', Integer, ForeignKey('media.id'), primary_key=True),
    Column('title', Unicode(255), nullable=False),
    Column('subtitle', Unicode(255)),
    Column('description_plain', UnicodeText),
    Column('notes', UnicodeText),
    Column('author_name', Unicode(50), nullable=False),
    Column('tags', UnicodeText),
    Column('topics', UnicodeText),
    mysql_engine='MyISAM',
)

# Columns grouped by their FULLTEXT index
_search_cols = {
    'public': [
        media_fulltext.c.title, media_fulltext.c.subtitle,
        media_fulltext.c.tags, media_fulltext.c.topics,
        media_fulltext.c.description_plain, media_fulltext.c.notes,
    ],
    'admin': [
        media_fulltext.c.title, media_fulltext.c.subtitle,
        media_fulltext.c.tags, media_fulltext.c.topics,
        media_fulltext.c.description_plain,
    ],
}
_search_param = sql.bindparam('search')


class MediaQuery(Query):
    def reviewed(self, flag=True):
        return self.filter(Media.reviewed == flag)

    def encoded(self, flag=True):
        return self.filter(Media.encoded == flag)

    def published(self, flag=True):
        published = sql.and_(
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

    def search(self, search):
        return self.join(MediaFullText)\
                   .filter(_MatchAgainstClause(_search_cols['public'], _search_param, True))\
                   .order_by(MediaFullText.relevance.desc())\
                   .params({_search_param.key: search})

    def admin_search(self, search):
        return self.join(MediaFullText)\
                   .filter(_MatchAgainstClause(_search_cols['admin'], _search_param, True))\
                   .order_by(MediaFullText.admin_relevance.desc())\
                   .params({_search_param.key: search})


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

    .. attribute:: topics

        A list of :class:`mediacore.model.topics.Topic`.

        See the :meth:`set_topics` helper.

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

    def set_topics(self, topics):
        """Set the topics relations of this media.

        :param topics: A list or comma separated string of tags to use.
        """
        if isinstance(topics, list):
            topics = fetch_topics(topics)
        self.topics = topics or []

    def reposition_file(self, file, budge_infront=None):
        """Position the first file after the second or last file.

        If only one file is specified, we move it to the last position (the end).

        If two files are specified, the first takes the seconds position, and the
        positions of the second file and those that follow it are incremented.

        This increments MediaFile.position such that gaps in the sequence occur.

        When the primary_file is changed by this operation, we ensure that the
        Media.type matches the type of the new primary_file.

        Depending on the situation, we manipulate the DBSession, rather than our
        usual practice of simply modifying the object and leaving DBSession work
        to the controller. This is necessary because we run a query on the DB
        without using the ORM in some cases.

        :param file: The file to move
        :type file: :class:`MediaFile` or int
        :param budge_infront: The file to position after.
        :type budge_infront: :class:`MediaFile` or int or None
        """
        if not isinstance(file, MediaFile):
            file = [f for f in self.files if f.id == file][0]

        if budge_infront:
            # The first file is going to move in front of the second
            if not isinstance(budge_infront, MediaFile):
                budge_infront = [f for f in self.files if f.id == budge_infront][0]

            pos = budge_infront.position
            is_first = budge_infront is self.primary_file

            # Update the moved row, the budge_infront file, and those after it.
            # When we reach the moved row, the new position is simply set,
            # otherwise the position is incremented 1.
            update = media_files.update()\
                .where(sql.and_(
                    media_files.c.media_id == self.id,
                    sql.or_(
                        media_files.c.position >= pos,
                        media_files.c.id == file.id
                    )
                ))\
                .values({
                    media_files.c.position: sql.case(
                        [(media_files.c.id == file.id, pos)],
                        else_=media_files.c.position + 1
                    )
                })

            DBSession.execute(update)
            datamanager.mark_changed(DBSession())

        else:
            # No budging, so if there any other files we'll have to go after them...
            pos = 0
            is_first = True

            if self.files:
                pos += self.files[-1].position
                is_first = False

            file.position = pos
            DBSession.add(file)

        # Making an audio file primary over a video file changes the media type
        if is_first and file.medium is not None:
            self.type = file.medium

        return pos

    def update_type(self):
        """Ensure the media type is that of the :attr:`Media.primary_file`."""
        primary_file = self.primary_file
        self.type = primary_file.medium if primary_file else None

    def update_status(self):
        """Ensure the reviewed, encoded, publishable flags make sense.

        * ``unreviewed`` is added if no files exist.
        * ``unencoded`` is added if there isn't any file to play with the
          Flash player. YouTube and other embeddable files qualify.
        * ``unencoded`` is added if this is a podcast episode, and there
          is no iTunes-compatible file. Embeddable file types don't qualify.
        * ``publish`` is removed and ``draft`` is added if any of
          ``unencoded``, ``unreviewed``, or ``draft`` are found.

        """
        self._validate_review_status()
        self._validate_encoding_status()
        self._validate_publish_status()

    def _validate_review_status(self):
        if not self.files:
            self.reviewed = True

    def _validate_encoding_status(self):
        if self.files:
            if not self.type:    # Sanity check
                self.update_type()
            for file in self.files:
                if file.type in config.playable_types[self.type]:
                    self.encoded = True
                    return True
            if self.podcast_id is None:
                for file in self.files:
                    if file.is_embeddable:
                        self.encoded = True
                        return True
        self.encoded = False
        return False

    def _validate_publish_status(self):
        if not self.reviewed or not self.encoded:
            self.publishable = False

    @property
    def primary_file(self):
        """The primary MediaFile to represent this Media object.

        None, if no files are marked with enable_player.

        TODO: Re-evaluate the uses of this property, some could be relying on
              unsafe unsumptions?
        """
        for file in self.files:
            if file.enable_player:
                return file
        return None

    @property
    def downloadable_file(self):
        """The MediaFile users can download for this Media object.

        None, if no files are of a type other than flv.
        """
        for file in self.files:
            if not file.is_embeddable and file.type != 'flv':
                return file
        return None


    @property
    def playable_files(self):
        return [file for file in self.files if file.enable_player]

    @property
    def feedable_files(self):
        return [file for file in self.files if file.enable_feed]

    @property
    def is_published(self):
        return self.publishable\
           and (self.publish_on is not None and self.publish_on <= datetime.now())\
           and (self.publish_until is None or self.publish_until >= datetime.now())

    def increment_views(self):
        # update the number of views with an expression, to avoid concurrency
        # issues associated with simultaneous writes.
        views = self.views + 1
        self.views = media.c.views + sql.text('1')
        return views

    def increment_likes(self):
        self.update_rating()
        # update the number of likes with an expression, to avoid concurrency
        # issues associated with simultaneous writes.
        likes = self.likes + 1
        self.likes = media.c.likes + sql.text('1')
        return likes

    def update_rating(self):
        # FIXME: The current algorithm assumes that the earliest publication
        #        date is January 1, 2000.

        # In our ranking algorithm, being base_life_hours newer is equivalent
        # to having log_base times more votes.
        log_base = int(fetch_setting('popularity_decay_exponent'))
        base_life_hours = int(fetch_setting('popularity_decay_lifetime'))

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


def create_media_stub():
    """Return a new :class:`Media` instance with helpful defaults.

    This is used any time we need a placeholder db record, such as when:

        * Some admin adds a file *before* saving their new media
        * Some admin uploads a thumbnail *before* saving their new media

    """
    user = request.environ['repoze.who.identity']['user']
    timestamp = datetime.now().strftime('%b-%d-%Y')
    m = Media()
    m.slug = get_available_slug(Media, 'stub-%s' % timestamp)
    m.title = '(Stub %s created by %s)' % (timestamp, user.display_name)
    m.author = Author(user.display_name, user.email_address)
    return m


class MediaFile(object):
    """
    Audio or Video file or link

    Represents a locally- or remotely- hosted file or an embeddable YouTube video.

    """

    def __repr__(self):
        return '<MediaFile: type=%s url=%s>' % (self.type, self.url)

    @property
    def mimetype(self):
        """The best-guess mimetype for this file type.

        Defaults to 'application/octet-stream'.
        """
        return config.mimetype_lookup.get('.' + self.type, 'application/octet-stream')

    @property
    def is_embeddable(self):
        """True if this file is embedded from another site, ex Youtube, Vimeo."""
        return self.type in config.embeddable_filetypes

    @property
    def is_playable(self):
        """True if this file can be played in most browsers (& is not embedded)."""
        for playable_types in config.playable_types.itervalues():
            if self.type in playable_types:
                return True
        return False

    def play_url(self, qualified=False):
        """The URL for use when embedding the media file in a page

        This MAY return a different URL than the link_url property.
        """
        if self.is_embeddable:
            return config.embeddable_filetypes[self.type]['play'] % self.url
        elif urlparse(self.url)[1]:
            return self.url.encode('utf-8')   # Full URL specified
        else:
            return helpers.url_for(controller='/media', action='serve',
                                   slug=self.media.slug, id=self.id,
                                   type=self.type, qualified=qualified)

    def link_url(self, qualified=False):
        """The URL for use when linking to a media file.

        This is usually a direct link to the file, but for youtube videos and
        other files marked as embeddable, this may return a link to the hosting
        site's view page.

        This MAY return a different URL than the play_url property.
        """
        if self.is_embeddable:
            return config.embeddable_filetypes[self.type]['link'] % self.url
        elif urlparse(self.url)[1]:
            return self.url.encode('utf-8')   # Full URL specified
        else:
            return helpers.url_for(controller='/media', action='serve',
                                   slug=self.media.slug, id=self.id,
                                   type=self.type, qualified=qualified)

    @property
    def medium(self):
        """Helper for determining whether this file is audio or video."""
        mimetype = self.mimetype
        if mimetype.startswith('audio'):
            return 'audio'
        elif mimetype.startswith('video'):
            return 'video'
        elif self.is_embeddable:
            return 'video'
        else:
            return None

    @validates('enable_feed')
    def _validate_enable_feed(self, key, on):
        """Ensure that modifications to the enable_feed prop won't break things.

        You cannot disable the last feed-enable file of a podcast episode.
        """
        if (not on and self.media and self.media.podcast_id
            and len([f for f in self.media.files if f.enable_feed]) == 1):
            raise MediaException, ('Published podcast media requires '
                                   'at least one file be feed-enabled.')
        return on


class MediaFullText(object):
    query = DBSession.query_property()


mapper(MediaFile, media_files)

mapper(MediaFullText, media_fulltext, properties={
    'relevance': column_property(_MatchAgainstClause(_search_cols['public'], _search_param, False), deferred=True),
    'admin_relevance': column_property(_MatchAgainstClause(_search_cols['admin'], _search_param, False), deferred=True),
})

_media_mapper = mapper(Media, media, properties={
    'fulltext': relation(MediaFullText, uselist=False, passive_deletes=True),
    'author': composite(Author, media.c.author_name, media.c.author_email),
    'files': relation(MediaFile, backref='media', order_by=media_files.c.position.asc(), passive_deletes=True),
    'tags': relation(Tag, secondary=media_tags, backref='media', collection_class=TagList, passive_deletes=True),
    'topics': relation(Topic, secondary=media_topics, backref='media', collection_class=TopicList, passive_deletes=True),

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
        media.c.publishable,
        media.c.publish_on <= datetime.now(),
        sql.or_(media.c.publish_until == None,
                media.c.publish_until >= datetime.now()),
    ]),
))

# Add properties for counting how many media items have a given Topic
_topics_mapper = class_mapper(Topic, compile=False)
_topics_mapper.add_properties(_properties_dict_from_labels(
    _mtm_count_property('media_count', media_topics),
    _mtm_count_property('media_count_published', media_topics, [
        media.c.publishable,
        media.c.publish_on <= datetime.now(),
        sql.or_(media.c.publish_until == None,
                media.c.publish_until >= datetime.now()),
    ]),
))
