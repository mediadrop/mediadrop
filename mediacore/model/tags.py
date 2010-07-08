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
import re

from datetime import datetime
from sqlalchemy import Table, ForeignKey, Column, sql, func
from sqlalchemy.types import Unicode, UnicodeText, Integer, DateTime, Boolean, Float
from sqlalchemy.orm import mapper, relation, backref, synonym, interfaces, validates, column_property

from mediacore.lib.helpers import excess_whitespace
from mediacore.model import slug_length, slugify, _mtm_count_property
from mediacore.model.meta import Base, DBSession


tags = Table('tags', Base.metadata,
    Column('id', Integer, autoincrement=True, primary_key=True),
    Column('name', Unicode(50), unique=True, nullable=False),
    Column('slug', Unicode(slug_length), unique=True, nullable=False),
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
    query = DBSession.query_property()

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

mapper(Tag, tags, order_by=tags.c.name)

def extract_tags(string):
    """Convert a comma separated string into a list of tag names.

    NOTE: The space-stripping here is necessary to patch a leaky abstraction.
          MySQL's string comparison with varchar columns is pretty fuzzy
          when it comes to space characters, and is even inconsistent between
          versions. We strip all preceding/trailing/duplicated spaces to be
          safe.

    """
    # count linebreaks as commas -- we assume user negligence
    string = string.replace("\n", ',')
    # strip repeating whitespace with a single space
    string = excess_whitespace.sub(' ', string)
    # make a tags list without any preceding and trailing whitespace
    tags = [tag.strip() for tag in string.split(',')]
    # remove duplicate and empty tags
    tags = set(tag for tag in tags if tag)
    return list(tags)

def fetch_and_create_tags(tag_names):
    """Return a list of Tag instances that match the given names.

    Tag names that don't yet exist are created automatically and
    returned alongside the results that did already exist.

    If you try to create a new tag that would have the same slug
    as an already existing tag, the existing tag is used instead.

    :param tag_names: The display :attr:`Tag.name`
    :type tag_names: list
    :returns: A list of :class:`Tag` instances.
    :rtype: :class:`TagList` instance

    """
    results = TagList()
    lower_names = [name.lower() for name in tag_names]
    slugs = [slugify(name) for name in lower_names]
    matches = Tag.query.filter(sql.or_(func.lower(Tag.name).in_(lower_names),
                                       Tag.slug.in_(slugs)))
    for tag in matches:
        results.append(tag)
        # Remove the match from our three lists until its completely gone
        while True:
            try:
                try:
                    index = slugs.index(tag.slug)
                except ValueError:
                    index = lower_names.index(tag.name.lower())
                tag_names.pop(index)
                lower_names.pop(index)
                slugs.pop(index)
            except ValueError:
                break
    if tag_names:
        new_tags = [{'name': n, 'slug': s} for n, s in zip(tag_names, slugs)]
        DBSession.execute(tags.insert(), new_tags)
        DBSession.flush()
        results += Tag.query.filter(Tag.slug.in_(slugs)).all()
    return results
