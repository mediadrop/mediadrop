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

import transaction
from datetime import datetime
from urlparse import urlparse
from sqlalchemy import Table, ForeignKey, Column, sql, func
from sqlalchemy.types import String, Unicode, UnicodeText, Integer, DateTime, Boolean, Float
from sqlalchemy.orm import mapper, class_mapper, relation, backref, synonym, composite, column_property, comparable_property, validates, collections
from tg import config, request
from zope.sqlalchemy import datamanager

from mediacore.model import DeclarativeBase, metadata, DBSession, get_available_slug, _mtm_count_property, _properties_dict_from_labels
from mediacore.model.authors import Author
from mediacore.model.comments import Comment, CommentTypeExtension, comment_count_property, comments
from mediacore.model.tags import Tag, TagList, tags, extract_tags, fetch_and_create_tags, tag_count_property
from mediacore.model.topics import Topic, TopicList, topics, fetch_topics, topic_count_property
from mediacore.model.status import Status, StatusType, status_column_property, status_where
from mediacore.lib import helpers

class MediaStatus(Status):
    values = ('trash', 'publish', 'draft', 'unencoded', 'unreviewed')

class MediaException(Exception): pass
class MediaFileException(MediaException): pass
class UnknownFileTypeException(MediaFileException): pass


media = Table('media', metadata,
    Column('id', Integer, autoincrement=True, primary_key=True),
    Column('type', String(10), nullable=False),
    Column('slug', String(50), unique=True, nullable=False),
    Column('status', StatusType(MediaStatus), default=MediaStatus('publish'), nullable=False),
    Column('podcast_id', Integer, ForeignKey('podcasts.id', onupdate='CASCADE', ondelete='CASCADE')),

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

media_comments = Table('media_comments', metadata,
    Column('media_id', Integer, ForeignKey('media.id', onupdate='CASCADE', ondelete='CASCADE'),
        primary_key=True),
    Column('comment_id', Integer, ForeignKey('comments.id', onupdate='CASCADE', ondelete='CASCADE'),
        primary_key=True, unique=True)
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
)


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

    .. attribute:: status

        An unordered set of flags:

            * ``trash`` if the file has been deleted.
            * ``publish`` if the media is ready to be displayed publicly. Note,
              however, that :attr:`Media.publish_on` and :attr:`Media.publish_until`
              also effect whether this object is actually displayed.
            * ``draft`` if we aren't ready for ``publish``.
            * ``unencoded`` if there are no web-friendly files for this object.
            * ``unreviewed`` if the content has not had an editorial review yet.

        See :meth:`update_status` for status validation rules.

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

        A list of :class:`mediacore.model.comments.Comment`.

        .. todo:: Reimplement as a dynamic loader.

    .. attribute:: comment_count
    .. attribute:: comment_count_published
    .. attribute:: comment_count_unreviewed
    .. attribute:: comment_count_trash

    """

    def __init__(self):
        if self.author is None:
            self.author = Author()
        if self.status is None:
            self.status = MediaStatus()

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
        """Examine :attr:`Media.status` to ensure it is an allowable value.

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
            self.status.add('unreviewed')
        return 'unreviewed' in self.status

    def _validate_encoding_status(self):
        if self.files:
            if not self.type:    # Sanity check
                self.update_type()
            for file in self.files:
                if file.type in config.playable_types[self.type]:
                    self.status.discard('unencoded')
                    return True
            if self.podcast_id is None:
                for file in self.files:
                    if file.is_embeddable:
                        self.status.discard('unencoded')
                        return True
        self.status.add('unencoded')
        return False

    def _validate_publish_status(self):
        if self.status.intersection(('unencoded', 'unreviewed', 'draft')):
            self.status.discard('publish')
            self.status.add('draft')
        return 'publish' in self.status

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
            if file.type != 'flv':
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
        return 'publish' in self.status\
           and 'trash' not in self.status\
           and (self.publish_on is not None and self.publish_on <= datetime.now())\
           and (self.publish_until is None or self.publish_until >= datetime.now())

    @property
    def is_unencoded(self):
        return 'unencoded' in self.status

    @property
    def is_unreviewed(self):
        return 'unreviewed' in self.status

    @property
    def is_draft(self):
        return 'draft' in self.status

    @property
    def is_trash(self):
        return 'trash' in self.status

    def increment_views(self):
        self.views = media.c.views + sql.text('1')


def create_media_stub():
    """Return a new :class:`Media` instance with helpful defaults.

    This is used any time we need a placeholder db record, such as when:

        * Some admin adds a file *before* saving their new media
        * Some admin uploads album art *before* saving their new media

    """
    user = request.environ['repoze.who.identity']['user']
    timestamp = datetime.now().strftime('%b-%d-%Y')
    m = Media()
    m.slug = get_available_slug(Media, 'stub-%s' % timestamp)
    m.title = '(Stub %s created by %s)' % (timestamp, user.display_name)
    m.author = Author(user.display_name, user.email_address)
    m.status = 'draft,unencoded,unreviewed'
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

    @property
    def play_url(self):
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
                                   type=self.type)

    @property
    def link_url(self):
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
                                   type=self.type)

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


mapper(MediaFile, media_files)

_media_mapper = mapper(Media, media, properties={
    'status': status_column_property(media.c.status),
    'author': composite(Author, media.c.author_name, media.c.author_email),
    'files': relation(MediaFile, backref='media', order_by=media_files.c.position.asc(), passive_deletes=True),
    'tags': relation(Tag, secondary=media_tags, backref='media', collection_class=TagList),
    'topics': relation(Topic, secondary=media_topics, backref='media', collection_class=TopicList),
    'comments': relation(Comment, secondary=media_comments, backref=backref('media', uselist=False),
        extension=CommentTypeExtension('media'), single_parent=True, passive_deletes=True),
})

# Add comment_count, comment_count_published, ... column properties to Media
_media_mapper.add_properties(_properties_dict_from_labels(
    comment_count_property('comment_count', media_comments),
    comment_count_property('comment_count_published', media_comments, [
        comments.c.publishable == True,
    ]),
    comment_count_property('comment_count_unreviewed', media_comments, [
        comments.c.reviewed == False,
    ]),
    comment_count_property('comment_count_trash', media_comments, [
        comments.c.reviewed == True, comments.c.publishable == False
    ]),
))

# Add properties for counting how many media items have a given Tag
_tags_mapper = class_mapper(Tag, compile=False)
_tags_mapper.add_properties(_properties_dict_from_labels(
    tag_count_property('media_count', media_tags, status_where(
        media.c.status, exclude='trash'
    )),
    tag_count_property('published_media_count', media_tags, status_where(
        media.c.status, include='publish', exclude='trash'
    )),
))

# Add properties for counting how many media items have a given Topic
_topics_mapper = class_mapper(Topic, compile=False)
_topics_mapper.add_properties(_properties_dict_from_labels(
    topic_count_property('media_count', media_topics, status_where(
        media.c.status, exclude='trash'
    )),
    topic_count_property('published_media_count', media_topics, status_where(
        media.c.status, include='publish', exclude='trash'
    )),
))
