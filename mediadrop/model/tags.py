# This file is a part of MediaDrop (http://www.mediadrop.net),
# Copyright 2009-2013 MediaDrop contributors
# For the exact contribution history, see the git revision log.
# The source code contained in this file is licensed under the GPLv3 or
# (at your option) any later version.
# See LICENSE.txt in the main project directory, for more information.
"""
Tag-based Categorization

Content can be labelled in an ad-hoc fashion with tags. Typically tags will
be displayed on the frontend using a 'tag cloud', rather than listing all
tags. This means you can tag all you want!
"""

import re

from itertools import izip
from sqlalchemy import Table, Column, sql, func
from sqlalchemy.types import Unicode, Integer
from sqlalchemy.orm import mapper, validates

from mediadrop.model import SLUG_LENGTH, slugify
from mediadrop.model.meta import DBSession, metadata
from mediadrop.plugin import events


tags = Table('tags', metadata,
    Column('id', Integer, autoincrement=True, primary_key=True),
    Column('name', Unicode(50), unique=True, nullable=False),
    Column('slug', Unicode(SLUG_LENGTH), unique=True, nullable=False),
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
        return '<Tag: %r>' % self.name

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

mapper(Tag, tags, order_by=tags.c.name, extension=events.MapperObserver(events.Tag))

excess_whitespace = re.compile('\s\s+', re.M)

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
    lower_names = [name.lower() for name in tag_names]
    slugs = [slugify(name) for name in lower_names]

    # Grab all the tags that exist already, whether its the name or slug
    # that matches. Slugs can be changed by the tag settings UI so we can't
    # rely on each tag name evaluating to the same slug every time.
    results = Tag.query.filter(sql.or_(func.lower(Tag.name).in_(lower_names),
                                       Tag.slug.in_(slugs))).all()

    # Filter out any tag names that already exist (case insensitive), and
    # any tag names evaluate to slugs that already exist.
    for tag in results:
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

    # Any remaining tag names need to be created.
    if tag_names:
        # We may still have multiple tag names which evaluate to the same slug.
        # Load it into a dict so that duplicates are overwritten.
        uniques = dict((slug, name) for slug, name in izip(slugs, tag_names))
        # Do a bulk insert to create the tag rows.
        new_tags = [{'name': n, 'slug': s} for s, n in uniques.iteritems()]
        DBSession.execute(tags.insert(), new_tags)
        DBSession.flush()
        # Query for our newly created rows and append them to our result set.
        results += Tag.query.filter(Tag.slug.in_(uniques.keys())).all()

    return results
