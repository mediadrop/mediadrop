from datetime import datetime
from sqlalchemy import Table, ForeignKey, Column
from sqlalchemy.types import String, Unicode, UnicodeText, Integer, DateTime, Boolean, Float
from sqlalchemy.orm import mapper, relation, backref, synonym, interfaces, validates

from mediaplex.model import DeclarativeBase, metadata, DBSession
from mediaplex.lib.helpers import slugify


tags = Table('tags', metadata,
    Column('id', Integer, autoincrement=True, primary_key=True),
    Column('name', Unicode(50), unique=True, nullable=False),
    Column('slug', Unicode(50), unique=True, nullable=False),
    mysql_engine='InnoDB',
    mysql_charset='utf8'
)


class Tag(object):
    """Tag definition"""

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


def extract_tags(string):
    return [tag.strip() for tag in string.split(',')]

def fetch_and_create_tags(tag_names):
    new_tags = []
    existing_tags = DBSession.query(Tag).filter(Tag.name.in_(tag_names)).all()
    existing_names = [tag.name for tag in existing_tags]
    tag_names = [tn for tn in tag_names if tn not in existing_names]
    conn = DBSession.connection()
    for tag_name in tag_names:
        new_tags.append({'name': tag_name, 'slug': slugify(tag_name)})
    if new_tags:
        conn.execute(tags.insert(), new_tags)
        existing_tags += DBSession.query(Tag).filter(Tag.name.in_(tag_names)).all()
    return existing_tags


class TagCollection(list):
    def __unicode__(self):
        return ', '.join([tag.name for tag in self.values()])


mapper(Tag, tags)
