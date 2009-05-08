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
from sqlalchemy import Table, ForeignKey, Column, sql
from sqlalchemy.types import String, Unicode, UnicodeText, Integer, DateTime, Boolean, Float
from sqlalchemy.orm import mapper, relation, backref, synonym, composite, column_property, comparable_property, validates

from mediaplex.model import DeclarativeBase, metadata, DBSession
from mediaplex.model.authors import Author
from mediaplex.model.rating import Rating
from mediaplex.model.comments import Comment, CommentTypeExtension
from mediaplex.model.tags import Tag, TagCollection, extract_tags, fetch_and_create_tags
from mediaplex.model.status import Status, StatusSet, StatusComparator, StatusType, StatusTypeExtension


TRASH = Status('trash', 1)
PUBLISH = Status('publish', 2)
DRAFT = Status('draft', 4)
PENDING_ENCODING = Status('pending_encoding', 8)
PENDING_REVIEW = Status('pending_review', 16)

STATUSES = dict((int(s), s) for s in (TRASH, PUBLISH, DRAFT, PENDING_ENCODING, PENDING_REVIEW))
"""Dictionary of allowed statuses, bitmask value(int) => Status(unicode) instance"""

class VideoStatusSet(StatusSet):
    _valid_els = STATUSES


media = Table('media', metadata,
    Column('id', Integer, autoincrement=True, primary_key=True),
    Column('type', Unicode(10), nullable=False),
    Column('slug', Unicode(50), unique=True, nullable=False),
    Column('created_on', DateTime, default=datetime.now, nullable=False),
    Column('modified_on', DateTime, default=datetime.now, onupdate=datetime.now, nullable=False),
    Column('publish_on', DateTime),
    Column('status', StatusType(VideoStatusSet), default=PUBLISH, nullable=False),
    Column('title', Unicode(50), nullable=False),
    Column('description', UnicodeText),
    Column('notes', UnicodeText),
    Column('duration', Integer, default=0, nullable=False),
    Column('views', Integer, default=0, nullable=False),
    Column('upload_url', Unicode(255)),
    Column('url', Unicode(255)),
    Column('author_name', Unicode(50), nullable=False),
    Column('author_email', Unicode(255), nullable=False),
    Column('rating_sum', Integer, default=0, nullable=False),
    Column('rating_votes', Integer, default=0, nullable=False),
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
    """Base class for Audio and Video"""
    def __init__(self):
        if self.author is None:
            self.author = Author()

    def __repr__(self):
        return '<Media: %s>' % self.slug

    def set_tags(self, tags):
        if isinstance(tags, basestring):
            tags = extract_tags(tags)
            tags = fetch_and_create_tags(tags)
        self.tags = tags or []


class Video(Media):
    def __repr__(self):
        return '<Video: %s>' % self.slug


class Audio(Media):
    def __repr__(self):
        return '<Audio: %s>' % self.slug


media_mapper = mapper(Media, media, polymorphic_on=media.c.type, properties={
    'status': column_property(media.c.status, extension=StatusTypeExtension(), comparator_factory=StatusComparator),
    'author': composite(Author, media.c.author_name, media.c.author_email),
    'rating': composite(Rating, media.c.rating_sum, media.c.rating_votes),
    'tags': relation(Tag, secondary=media_tags, backref='media', collection_class=TagCollection),
#TODO: Reimplement as a dynamic_loader instead of a relation. Better performance for larger datasets.
#      Just need to rethink the CommentTypeMapper because dyamic_loaders don't support extensions.
    'comments': relation(Comment, secondary=media_comments, backref=backref('media', uselist=False),
        extension=CommentTypeExtension(u'media'), single_parent=True, passive_deletes=True),
})
mapper(Audio, inherits=media_mapper, polymorphic_identity=u'audio')
mapper(Video, inherits=media_mapper, polymorphic_identity=u'video')
