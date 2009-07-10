"""
Media Models for Audio and Video

Things to be aware of:

  - Polymorphism is used to return Audio or Video objects while dealing with
    a single database table. Both these classes inherit the Media base class.

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

from datetime import datetime
from urlparse import urlparse
from sqlalchemy import Table, ForeignKey, Column, sql, and_, or_, func
from sqlalchemy.types import String, Unicode, UnicodeText, Integer, DateTime, Boolean, Float
from sqlalchemy.orm import mapper, class_mapper, relation, backref, synonym, composite, column_property, comparable_property, validates, collections
from tg import config

from mediaplex.model import DeclarativeBase, metadata, DBSession
from mediaplex.model.authors import Author
from mediaplex.model.rating import Rating
from mediaplex.model.comments import Comment, CommentTypeExtension, comments, PUBLISH as COMMENT_PUBLISH, TRASH as COMMENT_TRASH
from mediaplex.model.tags import Tag, TagCollection, tags, extract_tags, fetch_and_create_tags
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

    Column('title', Unicode(50), nullable=False),
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
    Column('order', Integer, default=0, nullable=False),
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

    @property
    def is_unreviewed(self):
        return UNREVIEWED in self.status

    @property
    def is_draft(self):
        return DRAFT in self.status

    @property
    def is_trash(self):
        return TRASH in self.status


class Video(Media):
    ENCODED_TYPE = 'flv'

    def __repr__(self):
        return '<Video: %s>' % self.slug


class Audio(Media):
    ENCODED_TYPE = 'mp3'

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


mapper(MediaFile, media_files)

media_mapper = mapper(Media, media, polymorphic_on=media.c.type, properties={
    'status': column_property(media.c.status, extension=StatusTypeExtension(), comparator_factory=StatusComparator),
    'author': composite(Author, media.c.author_name, media.c.author_email),
    'rating': composite(Rating, media.c.rating_sum, media.c.rating_votes),
    'files': relation(MediaFile, backref='media', order_by=media_files.c.order.desc(), passive_deletes=True, collection_class=MediaFileList),
    'tags': relation(Tag, secondary=media_tags, backref='media', collection_class=TagCollection),
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
