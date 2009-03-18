from datetime import datetime
from sqlalchemy import Table, ForeignKey, Column
from sqlalchemy.types import String, Unicode, UnicodeText, Integer, DateTime, Boolean, Float
from sqlalchemy.orm import mapper, relation, backref, synonym, composite

from mediaplex.model import DeclarativeBase, metadata, DBSession
from mediaplex.model.author import Author
from mediaplex.model.rating import Rating
from mediaplex.model.comments import Comment, CommentTypeExtension
from mediaplex.model.tags import Tag


media = Table('media', metadata,
    Column('id', Integer, autoincrement=True, primary_key=True),
    Column('type', Unicode(10), nullable=False),
    Column('slug', Unicode(50), unique=True, nullable=False),
    Column('created_on', DateTime, default=datetime.now, nullable=False),
    Column('modified_on', DateTime, default=datetime.now, onupdate=datetime.now, nullable=False),
    Column('publish_on', DateTime),
    Column('status', Unicode(15), default='unreviewed', nullable=False),
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
    def __init__(self, slug=None, author=None):
        self.slug = slug
        self.title = slug
        self.author = author

    def __repr__(self):
        return '<Media: %s>' % self.slug


class Video(Media):
    def __repr__(self):
        return '<Video: %s>' % self.slug


class Audio(Media):
    def __repr__(self):
        return '<Audio: %s>' % self.slug



media_mapper = mapper(Media, media, polymorphic_on=media.c.type, properties={
    'author': composite(Author, media.c.author_name, media.c.author_email),
    'rating': composite(Rating, media.c.rating_sum, media.c.rating_votes),
    'tags': relation(Tag, secondary=media_tags, backref='media'),
    'comments': relation(Comment, secondary=media_comments, backref='parent',
        extension=CommentTypeExtension('media')),
#    'comment_count': column_property(select().label('comment_count'))
})
mapper(Audio, inherits=media_mapper, polymorphic_identity='audio')
mapper(Video, inherits=media_mapper, polymorphic_identity='video')


#        """ Loops over all mappers setting the comment type to the deepest match. """
#        media_instance = state.obj()
#        for mapper in media_mapper.polymorphic_iterator():
#            if isinstance(media_instance, mapper.class_):
#                value.type = mapper.polymorphic_identity
#        assert value.type
