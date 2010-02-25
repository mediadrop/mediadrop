# This file is a part of MediaCore, Copyright 2009 Simple Station Inc.
#
# MediaCore is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# MediaCore is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
Tag-based Categorization

Content can be labelled in an ad-hoc fashion with tags. Typically tags will
be displayed on the frontend using a 'tag cloud', rather than listing all
tags. This means you can tag all you want!

"""

from datetime import datetime
from sqlalchemy import Table, ForeignKey, Column, sql, func
from sqlalchemy.types import String, Unicode, UnicodeText, Integer, DateTime, Boolean, Float
from sqlalchemy.orm import mapper, relation, backref, synonym, interfaces, validates, column_property

from mediacore.model import DeclarativeBase, metadata, DBSession, slugify, _mtm_count_property


tags = Table('tags', metadata,
    Column('id', Integer, autoincrement=True, primary_key=True),
    Column('name', Unicode(50), unique=True, nullable=False),
    Column('slug', String(50), unique=True, nullable=False),
    mysql_engine='InnoDB',
    mysql_charset='utf8'
)


class Tag(object):
    """
    Tag (keyword) for labelling content

    .. attribute:: id

    .. attribute:: name

        Display name

    .. attribute:: slug

        A unique URL-friendly permalink string for looking up this object.

    .. attribute:: media_content

    .. attribute:: media_count_published

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


class TagList(list):
    """
    List for easy rendering

    Automatically prints the contained tags separated by commas::

        >>> tags = TagList(['abc', 'def', 'ghi'])
        >>> tags
        abc, def, ghi

    """
    def __unicode__(self):
        return ', '.join([tag.name for tag in self.values()])


mapper(Tag, tags)


def extract_tags(string):
    return [tag.strip() for tag in string.split(',')]

def fetch_and_create_tags(tag_names):
    # copy the tag_names list
    new_tag_names = tag_names[:]

    # find tag names that already exist (case insensitive match)
    # and remove those names from our list
    lower_case_tags = [t.lower() for t in new_tag_names]
    existing_tags = DBSession.query(Tag).\
        filter(
            func.lower(Tag.name).in_(lower_case_tags)
        ).all()
    for t in existing_tags:
        for n in new_tag_names[:]:
            if n.lower() == t.name.lower():
                new_tag_names.remove(n)
                break

    # create the tags that don't yet exist
    if new_tag_names:
        new_tags = [{'name': n, 'slug': slugify(n)} for n in new_tag_names]
        DBSession.connection().execute(tags.insert(), new_tags)
        DBSession.flush()
        existing_tags += DBSession.query(Tag)\
            .filter(
                Tag.slug.in_([t['slug'] for t in new_tags])
            ).all()

    return existing_tags

