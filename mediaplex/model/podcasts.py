"""
Podcast Models

Dependent on the Media module.

"""
from datetime import datetime
from sqlalchemy import Table, ForeignKey, Column, sql
from sqlalchemy.types import String, Unicode, UnicodeText, Integer, DateTime, Boolean, Float
from sqlalchemy.orm import mapper, relation, backref, synonym, composite, validates, dynamic_loader, column_property

from mediaplex.model import DeclarativeBase, metadata, DBSession, Author
from mediaplex.model.media import Media, media, TRASH as MEDIA_TRASH, PUBLISH as MEDIA_PUBLISH
from mediaplex.lib.helpers import slugify


podcasts = Table('podcasts', metadata,
    Column('id', Integer, autoincrement=True, primary_key=True),
    Column('slug', String(50), unique=True, nullable=False),
    Column('created_on', DateTime, default=datetime.now, nullable=False),
    Column('modified_on', DateTime, default=datetime.now, onupdate=datetime.now, nullable=False),
    Column('title', Unicode(50), nullable=False),
    Column('subtitle', Unicode(255)),
    Column('description', UnicodeText),
    Column('category', Unicode(50)),
    Column('author_name', Unicode(50), nullable=False),
    Column('author_email', Unicode(50), nullable=False),
    Column('explicit', Boolean, default=None),
    Column('copyright', Unicode(50)),
)


class Podcast(object):
    def __repr__(self):
        return '<Podcast: %s>' % self.slug

    @validates('slug')
    def validate_slug(self, key, slug):
        return slugify(slug)


mapper(Podcast, podcasts, properties={
    'author': composite(Author,
        podcasts.c.author_name,
        podcasts.c.author_email),
    'media': dynamic_loader(Media, backref='podcast'),
    'media_count':
        column_property(
            sql.select(
                [sql.func.count(media.c.id)],
                sql.and_(
                    media.c.podcast_id == podcasts.c.id,
                    media.c.status.op('&')(int(MEDIA_TRASH)) == 0 # status excludes 'trash'
                )
            ).label('media_count'),
            deferred=True
        ),
    'published_media_count':
        column_property(
            sql.select(
                [sql.func.count(media.c.id)],
                sql.and_(
                    media.c.podcast_id == podcasts.c.id,
                    media.c.status.op('&')(int(MEDIA_PUBLISH)) == int(MEDIA_PUBLISH), # status includes 'publish'
                    media.c.status.op('&')(int(MEDIA_TRASH)) == 0, # status excludes 'trash'
                )
            ).label('published_media_count'),
            deferred=True
        )
})
