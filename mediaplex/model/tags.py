from datetime import datetime
from sqlalchemy import Table, ForeignKey, Column, sql
from sqlalchemy.types import String, Unicode, UnicodeText, Integer, DateTime, Boolean, Float
from sqlalchemy.orm import mapper, relation, backref, synonym, interfaces, validates, column_property

from mediaplex.model import DeclarativeBase, metadata, DBSession, slugify, _mtm_count_property


tags = Table('tags', metadata,
    Column('id', Integer, autoincrement=True, primary_key=True),
    Column('name', Unicode(50), unique=True, nullable=False),
    Column('slug', String(50), unique=True, nullable=False),
    mysql_engine='InnoDB',
    mysql_charset='utf8'
)


class Tag(object):
    """Tag definition
    """
    def __init__(self, name=None, slug=None):
        self.name = name or None
        self.slug = slug or name or None

    def __repr__(self):
        return '<Tag: %s>' % self.name

    def __unicode__(self):
        return self.name

    @validates('slug')
    def validate_slug(self, key, slug):
        return slugify(slug)


class TagCollection(list):
    def __unicode__(self):
        return ', '.join([tag.name for tag in self.values()])


mapper(Tag, tags)


def extract_tags(string):
    return [tag.strip() for tag in string.split(',')]

def fetch_and_create_tags(tag_names):
    tag_dict = dict()
    for t in tag_names:
        tag_dict[slugify(t)] = t

    existing_tags = DBSession.query(Tag).filter(Tag.slug.in_(tag_dict.keys())).all()
    existing_slugs = [t.slug for t in existing_tags]
    new_slugs = [s for s in tag_dict.keys() if s not in existing_slugs]
    new_tags = [{'name': tag_dict[s], 'slug': s} for s in new_slugs]

    if new_tags:
        DBSession.connection().execute(tags.insert(), new_tags)
        DBSession.flush()
        existing_tags += DBSession.query(Tag).filter(Tag.slug.in_(new_slugs)).all()
    return existing_tags


tag_count_property = _mtm_count_property
