"""
Podcast Models

Dependent on the Media module.

"""
from datetime import datetime
from sqlalchemy import Table, ForeignKey, Column
from sqlalchemy.types import String, Unicode, UnicodeText, Integer, DateTime, Boolean, Float
from sqlalchemy.orm import mapper, relation, backref, synonym, composite, validates, dynamic_loader

from mediaplex.model import DeclarativeBase, metadata, DBSession, Author, Media
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
    Column('author_name', Unicode(50)),
    Column('author_email', Unicode(50)),
    Column('explicit', Boolean, default=False),
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
})
