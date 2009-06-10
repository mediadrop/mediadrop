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
from sqlalchemy import Table, ForeignKey, Column, sql, and_, or_, func
from sqlalchemy.types import String, Unicode, UnicodeText, Integer, DateTime, Boolean, Float
from sqlalchemy.orm import mapper, relation, backref, synonym, composite, column_property, comparable_property, validates, collections

from mediaplex.model import DeclarativeBase, metadata, DBSession
from mediaplex.model.authors import Author
from mediaplex.model.rating import Rating
from mediaplex.model.comments import Comment, CommentTypeExtension, comments
from mediaplex.model.tags import Tag, TagCollection, tags, extract_tags, fetch_and_create_tags
from mediaplex.model.status import Status, StatusSet, StatusComparator, StatusType, StatusTypeExtension
from mediaplex.lib.helpers import slugify


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
    Column('type', Unicode(10), nullable=False),
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
    Column('is_original', Boolean, default=False, nullable=False),
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
        return slugify(slug)


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


mapper(MediaFile, media_files)

media_mapper = mapper(Media, media, polymorphic_on=media.c.type, properties={
    'status': column_property(media.c.status, extension=StatusTypeExtension(), comparator_factory=StatusComparator),
    'author': composite(Author, media.c.author_name, media.c.author_email),
    'rating': composite(Rating, media.c.rating_sum, media.c.rating_votes),
    'files': relation(MediaFile, backref='media', passive_deletes=True),
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
                    comments.c.status.op('&')(2) == 2# note that 2 is the ID of the comments 'publish' STATUS
                )
            ).label('comment_count'),
            deferred=True
        )
})
mapper(Audio, inherits=media_mapper, polymorphic_identity='audio')
mapper(Video, inherits=media_mapper, polymorphic_identity='video')

tags_mapper = mapper(Tag, tags, properties={
    'media_count':
        column_property(
            sql.select(
                [sql.func.count(media_tags.c.tag_id)],
                and_(
                    media.c.id == media_tags.c.media_id,
                    tags.c.id == media_tags.c.tag_id,
                    media.c.status.op('&')(2) == 2 # note that 2 is the ID of the media 'publish' STATUS
                )
            ).label('media_count'),
            deferred=True
        )
})
