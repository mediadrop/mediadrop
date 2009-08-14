"""
Media Models for Audio and Video

Things to be aware of:

  - Polymorphism is used to return Audio or Video objects while dealing with
    a single database table. Both these classes inherit the Media base class.
    We also have a PlaceholderMedia type for media that hasn't yet been
    defined as one or the other.

  - To switch a row from one polymorphic type to another use change_media_type()

  - Media.author and Media.rating are composite columns and provide an interface
    similar to relations. In other words, author_name & author_email are shuffled
    into a single Author object.

    Example Author usage (ratings are the same):
       m = Video()
       m.author = Author()
       m.author.email = u'a@b.com'
       print m.author.email
       DBSession.add(m) # everything is saved

    This gives us the flexibility to properly normalize our author data without
    modifying all the places in the app where we access our author information.

  - For status documentation see mediaplex.model.status

"""

import transaction
from datetime import datetime
from urlparse import urlparse
from sqlalchemy import Table, ForeignKey, Column, sql, and_, or_, func, select
from sqlalchemy.types import String, Unicode, UnicodeText, Integer, DateTime, Boolean, Float
from sqlalchemy.orm import mapper, class_mapper, relation, backref, synonym, composite, column_property, comparable_property, validates, collections
from tg import config, request

from mediaplex.model import DeclarativeBase, metadata, DBSession, get_available_slug
from mediaplex.model.authors import Author
from mediaplex.model.rating import Rating
from mediaplex.model.comments import Comment, CommentTypeExtension, comments, PUBLISH as COMMENT_PUBLISH, TRASH as COMMENT_TRASH
from mediaplex.model.tags import Tag, TagCollection, tags, extract_tags, fetch_and_create_tags
from mediaplex.model.topics import Topic, TopicCollection, topics, fetch_topics
from mediaplex.model.status import Status, StatusSet, StatusComparator, StatusType, StatusTypeExtension
from mediaplex.lib import helpers


TRASH = Status('trash', 1)
PUBLISH = Status('publish', 2)
DRAFT = Status('draft', 4)
UNENCODED = Status('unencoded', 8)
UNREVIEWED = Status('unreviewed', 16)

STATUSES = dict((int(s), s) for s in (TRASH, PUBLISH, DRAFT, UNENCODED, UNREVIEWED))
"""Dictionary of allowed statuses, bitmask value(int) => Status(unicode) instance"""

class MediaStatusSet(StatusSet):
    _valid_els = STATUSES

class MediaException(Exception): pass
class MediaFileException(MediaException): pass
class UnknownFileTypeException(MediaFileException): pass


media = Table('media', metadata,
    Column('id', Integer, autoincrement=True, primary_key=True),
    Column('type', String(10), nullable=False),
    Column('slug', String(50), unique=True, nullable=False),
    Column('status', StatusType(MediaStatusSet), default=PUBLISH, nullable=False),
    Column('podcast_id', Integer, ForeignKey('podcasts.id', onupdate='CASCADE', ondelete='CASCADE')),

    Column('created_on', DateTime, default=datetime.now, nullable=False),
    Column('modified_on', DateTime, default=datetime.now, onupdate=datetime.now, nullable=False),
    Column('publish_on', DateTime),
    Column('publish_until', DateTime),

    Column('title', Unicode(255), nullable=False),
    Column('subtitle', Unicode(255)),
    Column('description', UnicodeText),
    Column('notes', UnicodeText),

    Column('duration', Integer, default=0, nullable=False),
    Column('views', Integer, default=0, nullable=False),
    Column('rating_sum', Integer, default=0, nullable=False),
    Column('rating_votes', Integer, default=0, nullable=False),

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

    Column('position', Integer, default=0, nullable=False),
    Column('enable_player', Boolean, default=True, nullable=False),
    Column('enable_feed', Boolean, default=True, nullable=False),

    Column('created_on', DateTime, default=datetime.now, nullable=False),
    Column('modified_on', DateTime, default=datetime.now, onupdate=datetime.now, nullable=False),
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


class Media(object):
    """Audio and Video"""
    def __init__(self):
        if self.author is None:
            self.author = Author()
        if self.status is None:
            self.status = MediaStatusSet()

    def __repr__(self):
        return '<Media: %s>' % self.slug

    def set_tags(self, tags):
        if isinstance(tags, basestring):
            tags = extract_tags(tags)
            tags = fetch_and_create_tags(tags)
        self.tags = tags or []

    def set_topics(self, topics):
        if isinstance(topics, list):
            topics = fetch_topics(topics)
        self.topics = topics or []

    def reposition_file(self, file_id, prev_id):
        """Reorder the files so that the first file ID follows the second.

        If prev_id is None, or the prev_id does not exist, move to the top.
        """
        file = [f for f in self.files if f.id == file_id][0]
        try:
            pos = [f for f in self.files if f.id == prev_id][0].position
        except KeyError:
            pos = 1

        file.position = pos
        bump_others = media_files.update()\
            .where(and_(media_files.c.media_id == self.files[0].media_id,
                        media_files.c.position >= pos,
                        media_files.c.id != file_id))\
            .values({media_files.c.position: media_files.c.position + 1})

        DBSession.add(file)
        DBSession.execute(bump_others)
        return pos

    def update_type(self):
        """Ensure the media type is that of the first file."""
        if self.files:
            for file in self.files:
                file_medium = file.medium
                if file_medium is not None:
                    self.type = file_medium
                    return self.type
        self.type = None
        return None

    def update_status(self, add=None, discard=None, update=None):
        """Update and validate the status, ensuring we have a sane state.

        REVIEW
          Flag unreviewed if no files exist.

        ENCODING
          Flag encoded if one or more files is suitable, or flag unencoded.

          Media is generally encoded if any file type is in cls.ENCODED_TYPES or
          is embeddable, e.g. YouTube. However, media for podcasts are considered
          unencoded since YouTube videos cannot be included in RSS/iTunes.

        PUBLISH
          Flag unpublished if unencoded, unreviewed, or a draft.
        """
        if add:
            self.status.add(add)
        if discard:
            self.status.discard(discard)
        if update:
            self.status.update(update)

        self._validate_review_status()
        self._validate_encoding_status()
        self._validate_publish_status()

    def _validate_review_status(self):
        """Flag unreviewed if no files exist."""
        if not self.files:
            self.status.add(UNREVIEWED)
        return UNREVIEWED in self.status

    def _validate_encoding_status(self):
        """Flag encoded if one or more files is suitable, or flag unencoded.

        Media is generally encoded if any file type is in cls.ENCODED_TYPES or
        is embeddable, e.g. YouTube. However, media for podcasts are considered
        unencoded since YouTube videos cannot be included in RSS/iTunes.
        """
        if self.files:
            if not self.type:    # Sanity check
                self.update_type()
            for file in self.files:
                if file.type in config.playable_types[self.type]:
                    self.status.discard(UNENCODED)
                    return True
            if self.podcast_id is None:
                for file in self.files:
                    if file.is_embeddable:
                        self.status.discard(UNENCODED)
                        return True
        self.status.add(UNENCODED)
        return False

    def _validate_publish_status(self):
        """Flag unpublished if unencoded, unreviewed, or a draft."""
        if self.status.intersection((UNENCODED, UNREVIEWED, DRAFT)):
            self.status.discard(PUBLISH)
            self.status.add(DRAFT)
        return PUBLISH in self.status

    @property
    def primary_file(self):
        """The primary MediaFile to represent this Media object.

        None, if no files are marked with enable_player
        """
        enabled_files = [f for f in self.files if f.enable_player]
        if enabled_files:
            return enabled_files[0]
        else:
            return None

    @property
    def is_published(self):
        return PUBLISH in self.status\
           and TRASH not in self.status\
           and (self.publish_on is not None and self.publish_on <= datetime.now())\
           and (self.publish_until is None or self.publish_until >= datetime.now())

    @property
    def is_unencoded(self):
        return UNENCODED in self.status

    @property
    def is_unreviewed(self):
        return UNREVIEWED in self.status

    @property
    def is_draft(self):
        return DRAFT in self.status

    @property
    def is_trash(self):
        return TRASH in self.status


def create_media_stub():
    """Create a new placeholder Media instance."""
    user = request.environ['repoze.who.identity']['user']
    timestamp = datetime.now().strftime('%b-%d-%Y')
    m = Media()
    m.slug = get_available_slug(Media, 'stub-%s' % timestamp)
    m.title = '(Stub %s created by %s)' % (timestamp, user.display_name)
    m.author = Author(user.display_name, user.email_address)
    return m


class MediaFile(object):
    """Metadata of files which belong to a certain media item"""
    def __repr__(self):
        return '<MediaFile: type=%s url=%s>' % (self.type, self.url)

    @property
    def mimetype(self):
        return config.mimetype_lookup.get('.' + self.type, 'application/octet-stream')

    @property
    def is_embeddable(self):
        return self.type in config.embeddable_filetypes

    @property
    def play_url(self):
        """The URL for use when embedding the media file in a page

        This MAY return a different URL than
        the link_url property.
        """
        if self.is_embeddable:
            return config.embeddable_filetypes[self.type]['play'] % self.url
        elif urlparse(self.url)[1]:
            return self.url.encode('utf-8')   # Full URL specified
        else:
            return helpers.url_for(controller='/media', action='serve',
                                   slug=self.media.slug, type=self.type)

    @property
    def link_url(self):
        """The URL for use when linking to a media file.

        This is usually a direct link to the file, but for youtube videos and
        other files marked as embeddable, this may return a link to the hosting
        site's view page.

        This MAY return a different URL than
        the playurl property.
        """
        if self.is_embeddable:
            return config.embeddable_filetypes[self.type]['link'] % self.url
        elif urlparse(self.url)[1]:
            return self.url.encode('utf-8')   # Full URL specified
        else:
            return helpers.url_for(controller='/media', action='serve',
                                   slug=self.media.slug, type=self.type)

    @property
    def medium(self):
        """Helper for determining whether this file is audio or video"""
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
        if not on and self.media.podcast_id\
                  and len([f for f in self.media.files if f.enable_feed]) == 1:
            raise MediaException, 'Published podcast media requires '\
                'at least one file be feed-enabled.'
        return on


mapper(MediaFile, media_files)

media_mapper = mapper(Media, media, properties={
    'status': column_property(media.c.status, extension=StatusTypeExtension(), comparator_factory=StatusComparator),
    'author': composite(Author, media.c.author_name, media.c.author_email),
    'rating': composite(Rating, media.c.rating_sum, media.c.rating_votes),
    'files': relation(MediaFile, backref='media', order_by=media_files.c.position.asc(), passive_deletes=True),
    'tags': relation(Tag, secondary=media_tags, backref='media', collection_class=TagCollection),
    'topics': relation(Topic, secondary=media_topics, backref='media', collection_class=TopicCollection),
    'comments': relation(Comment, secondary=media_comments, backref=backref('media', uselist=False),
        extension=CommentTypeExtension('media'), single_parent=True, passive_deletes=True),
    'comment_count':
        column_property(
            sql.select(
                [sql.func.count(media_comments.c.comment_id)],
                and_(
                    media.c.id == media_comments.c.media_id,
                    comments.c.id == media_comments.c.comment_id,
                    comments.c.status.op('&')(int(COMMENT_PUBLISH)) == int(COMMENT_PUBLISH), # status includes 'publish'
                    comments.c.status.op('&')(int(COMMENT_TRASH)) == 0, # status excludes 'trash'
                )
            ).label('comment_count'),
            deferred=True
        )
})

tags_mapper = class_mapper(Tag, compile=False)
tags_mapper.add_property(
    'published_media_count',
    column_property(
        sql.select(
            [sql.func.count(media_tags.c.tag_id)],
            and_(
                media.c.id == media_tags.c.media_id,
                tags.c.id == media_tags.c.tag_id,
                media.c.status.op('&')(int(PUBLISH)) == int(PUBLISH), # status includes 'publish'
                media.c.status.op('&')(int(TRASH)) == 0, # status excludes 'trash'
            )
        ).label('published_media_count'),
       deferred=True
    )
)
tags_mapper.add_property(
    'media_count',
    column_property(
        sql.select(
            [sql.func.count(media_tags.c.tag_id)],
            and_(
                media.c.id == media_tags.c.media_id,
                tags.c.id == media_tags.c.tag_id,
                media.c.status.op('&')(int(TRASH)) == 0, # status excludes 'trash'
            )
        ).label('published_media_count'),
       deferred=True
    )
)

topics_mapper = class_mapper(Topic, compile=False)
topics_mapper.add_property(
    'published_media_count',
    column_property(
        sql.select(
            [sql.func.count(media_topics.c.topic_id)],
            and_(
                media.c.id == media_topics.c.media_id,
                topics.c.id == media_topics.c.topic_id,
                media.c.status.op('&')(int(PUBLISH)) == int(PUBLISH), # status includes 'publish'
                media.c.status.op('&')(int(TRASH)) == 0, # status excludes 'trash'
            )
        ).label('published_media_count'),
       deferred=True
    )
)
topics_mapper.add_property(
    'media_count',
    column_property(
        sql.select(
            [sql.func.count(media_topics.c.topic_id)],
            and_(
                media.c.id == media_topics.c.media_id,
                topics.c.id == media_topics.c.topic_id,
                media.c.status.op('&')(int(TRASH)) == 0, # status excludes 'trash'
            )
        ).label('published_media_count'),
       deferred=True
    )
)
