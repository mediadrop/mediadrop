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
from zope.sqlalchemy import datamanager
from tg import config

from mediaplex.model import DeclarativeBase, metadata, DBSession
from mediaplex.model.authors import Author
from mediaplex.model.rating import Rating
from mediaplex.model.comments import Comment, CommentTypeExtension, comments, PUBLISH as COMMENT_PUBLISH, TRASH as COMMENT_TRASH
from mediaplex.model.tags import Tag, TagCollection, tags, extract_tags, fetch_and_create_tags
from mediaplex.model.topics import Topic, TopicCollection, topics
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
    """Base class for Audio and Video

    :param comment_count:
      The number of comments on this Media, duh. Uses an optimized SQL query
      instead of loading the entire list of comments into memory and calling len().
      This field is not loaded by default, a separate query grabs it on first use.
      To populate it on the initial load include the following option:
          DBSession.query(Media).options(undefer('comment_count')).all()

    """
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

    @validates('slug')
    def validate_slug(self, key, slug):
        return helpers.slugify(slug)

    @property
    def is_published(self):
        return PUBLISH in self.status\
           and TRASH not in self.status\
           and (self.publish_on is not None and self.publish_on <= datetime.now())\
           and (self.publish_until is None or self.publish_until >= datetime.now())

    @property
    def is_unencoded(self):
        return UNENCODED in self.status

    def update_status(self):
        """Update the status to the most sane values"""
        self.update_review_status()
        self.update_encoding_status()
        self.update_publish_status()

    def update_review_status(self):
        if not self.files:
            self.status.add(UNREVIEWED)
        return UNREVIEWED in self.status

    def update_encoding_status(self):
        """Check if the media can be safely considered encoded"""
        if self.ENCODED_TYPES:
            for file in self.files:
                if file.type in self.ENCODED_TYPES:
                    self.status.discard(UNENCODED)
                    return True

            if self.podcast_id is None:
                for file in self.files:
                    if file.is_embeddable:
                        self.status.discard(UNENCODED)
                        return True

        self.status.update((UNENCODED, DRAFT))
        return False

    def update_publish_status(self):
        if self.status.intersection((UNENCODED, UNREVIEWED, DRAFT)):
            self.status.discard(PUBLISH)
        return PUBLISH in self.status

    @property
    def is_unreviewed(self):
        return UNREVIEWED in self.status

    @property
    def is_draft(self):
        return DRAFT in self.status

    @property
    def is_trash(self):
        return TRASH in self.status

    @property
    def is_new(self):
        return self.id is None


class PlaceholderMedia(Media):
    ENCODED_TYPES = None

    def __init__(self):
        self.status = (DRAFT, UNENCODED, UNREVIEWED)

    def __repr__(self):
        return '<PlaceholderMedia: %s>' % self.slug


class Video(Media):
    ENCODED_TYPES = ('flv', )

    def __repr__(self):
        return '<Video: %s>' % self.slug


class Audio(Media):
    ENCODED_TYPES = ('mp3', 'mp4', 'm4a')

    def __repr__(self):
        return '<Audio: %s>' % self.slug



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
        if self.is_embeddable:
            return config.embeddable_filetypes[self.type]['play'] % self.url
        elif urlparse(self.url)[1]:
            return self.url.encode('utf-8') # full URL specified
        else:
            return helpers.url_for(controller='/media', action='serve', slug=self.media.slug, type=self.type) # local file

    @property
    def link_url(self):
        if self.is_embeddable:
            return config.embeddable_filetypes[self.type]['link'] % self.url
        elif urlparse(self.url)[1]:
            return self.url.encode('utf-8') # full URL specified
        else:
            return helpers.url_for(controller='/media', action='serve', slug=self.media.slug, type=self.type) # local file

    @property
    def av(self):
        """Helper for determining whether this file is audio or video"""
        mimetype = self.mimetype
        if mimetype.startswith('audio'):
            return 'audio'
        elif mimetype.startswith('video'):
            return 'video'
        elif self.is_embeddable:
            return 'video' #NOTE: This isn't always a safe assumption
        else:
            raise UnknownFileTypeException, 'Could not determine whether the file is audio or video'


class MediaFileList(list):
    def for_player(self):
        picks = self.pick_types(['flv', 'mp3', 'mp4'])
        if picks:
            return picks[0]
        for file in self:
            if file.is_embeddable:
                return file
        return None

    def pick_types(self, types):
        """Return a list of files that match the given types in the order they are given"""
        picks = (file for file in self if file.type in types)
        return sorted(picks, key=lambda file: types.index(file.type))

    def reposition(self, file_id, prev_id):
        """Reorder the files so that the first file ID follows the second.
        If prev_id is None, the file is moved to the top"""
        file = [f for f in self if f.id == file_id][0]
        pos  = [f for f in self if f.id == prev_id][0].position if prev_id else 1

        file.position = pos
        bump_others = media_files.update()\
            .where(and_(media_files.c.media_id == self[0].media_id,
                        media_files.c.position >= pos,
                        media_files.c.id != file_id))\
            .values({media_files.c.position: media_files.c.position + 1})

        DBSession.add(file)
        DBSession.execute(bump_others)



def change_media_type(media_item, type, refresh=True):
    """UPDATE the polymorphic type of the given media.

    Results in the current transaction being committed, and
    old references to the given media_item will be unusable.

    media_item
      An ID or Media instance.

    type
      The polymorphic identity as a string or a Media subclass.

    refresh
      Indicates the given media should be reloaded from the
      database as its an instance of its new polymorphic subclass.
      Defaults to True.

    """
    if isinstance(media_item, Media):
        id = media_item.id
    else:
        id = int(media_item)
    if not isinstance(type, basestring):
        type = class_mapper(type, compile=False).polymorphic_identity

    result = DBSession.execute(media.update().where(media.c.id == id)\
                                             .values({media.c.type: type}))
    assert result.rowcount == 1, 'Changing media %s to type %s failed to '\
        'affect 1 single row (%d affected).' % (id, type, result.rowcount)

    # Manually executing queries on the session leaves it unchanged
    datamanager.mark_changed(DBSession())
    transaction.commit()

    if refresh:
        # Doesn't use query.get() since it seems to remember the polymorphic
        # identity of the given ID and automatically filters for that.
        return DBSession.query(Media).filter(media.c.id == id).one()
    else:
        return None


mapper(MediaFile, media_files)

media_mapper = mapper(Media, media, polymorphic_on=media.c.type, properties={
    'status': column_property(media.c.status, extension=StatusTypeExtension(), comparator_factory=StatusComparator),
    'author': composite(Author, media.c.author_name, media.c.author_email),
    'rating': composite(Rating, media.c.rating_sum, media.c.rating_votes),
    'files': relation(MediaFile, backref='media', order_by=media_files.c.position.asc(), passive_deletes=True, collection_class=MediaFileList),
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
mapper(PlaceholderMedia, inherits=media_mapper, polymorphic_identity='placeholder')
mapper(Audio, inherits=media_mapper, polymorphic_identity='audio')
mapper(Video, inherits=media_mapper, polymorphic_identity='video')



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
