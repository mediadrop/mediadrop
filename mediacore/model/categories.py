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

from collections import defaultdict
from datetime import datetime
from sqlalchemy import Table, ForeignKey, Column, sql
from sqlalchemy.types import String, Unicode, UnicodeText, Integer, DateTime, Boolean, Float
from sqlalchemy.orm import mapper, relation, backref, synonym, interfaces, validates, Query, attributes

from mediacore.model import metadata, DBSession, slugify


categories = Table('categories', metadata,
    Column('id', Integer, autoincrement=True, primary_key=True),
    Column('name', Unicode(50), unique=True, nullable=False),
    Column('slug', String(50), unique=True, nullable=False),
    Column('parent_id', Integer, ForeignKey('categories.id', onupdate='CASCADE', ondelete='CASCADE')),
    mysql_engine='InnoDB',
    mysql_charset='utf8'
)

def traverse(cats, depth=0):
    """Iterate through a depth-first traversal of the given categories.

    Yields a 2-tuple of the :class:`Category` instance and it's
    relative depth in the tree.

    """
    for cat in cats:
        yield cat, depth
        for subcat, subdepth in traverse(cat.children, depth + 1):
            yield subcat, subdepth

class CategoryQuery(Query):
    traverse = traverse
    """Iterate over all categories and nested children in depth-first order."""

    def all(self):
       return CategoryList(self)

    def roots(self):
        """Filter for just root, parentless categories."""
        return self.filter(Category.parent_id == None)

    def populated_tree(self):
        """Return the root categories with children populated to any depth.

        Adjacency lists are notoriously inefficient for fetching deeply
        nested trees, and since our dataset will always be reasonably
        small, this method should greatly improve efficiency. Only one
        query is necessary to fetch a tree of any depth. This isn't
        always the solution, but for some situations, it is worthwhile.

        For example, printing the entire tree can be done with one query::

            query = Category.query.options(undefer('media_count'))
            for cat, depth in query.populated_tree().traverse():
                print "    " * depth, cat.name, '(%d)' % cat.media_count

        Without this method, especially with the media_count undeferred,
        this would require a lot of extra queries for nested categories.

        """
        cats = self.all()
        roots = CategoryList()
        children = defaultdict(list)
        for cat in cats:
            if cat.parent_id:
                children[cat.parent_id].append(cat)
            else:
                roots.append(cat)
        for cat in cats:
            attributes.set_committed_value(cat, 'children', children[cat.id])
        return roots

class CategoryList(list):
    traverse = traverse
    """Iterate over all categories and nested children in depth-first order."""

    def __unicode__(self):
        return ', '.join(cat.name for cat in self.itervalues())

class Category(object):
    """
    Category Mapped Class
    """
    query = DBSession.query_property(CategoryQuery)

    def __init__(self, name=None, slug=None):
        self.name = name or None
        self.slug = slug or name or None

    def __repr__(self):
        return '<Category: %s>' % self.name

    def __unicode__(self):
        return self.name

    @validates('slug')
    def validate_slug(self, key, slug):
        return slugify(slug)

    def traverse(self):
        """Iterate over all nested categories in depth-first order."""
        return traverse(self.children)

    def descendants(self):
        """Return a list of descendants in depth-first order."""
        return [desc for desc, depth in self.traverse()]

    def ancestors(self):
        """Return a list of ancestors, starting with the root node.

        This method is optimized for when all categories have already
        been fetched in the current DBSession::

            >>> Category.query.all()    # run one query
            >>> row = Category.query.get(50)   # doesn't use a query
            >>> row.parent    # the DBSession recognized the primary key
            <Category: parent>
            >>> print row.ancestors()
            [...,
             <Category: great-grand-parent>,
             <Category: grand-parent>,
             <Category: parent>]

        """
        ancestors = CategoryList()
        anc = self.parent
        while anc:
            ancestors.insert(0, anc)
            anc = anc.parent
        return ancestors

    def depth(self):
        """Return this category's distance from the root of the tree."""
        return len(self.ancestors())



mapper(Category, categories, properties={
    'children': relation(Category,
        backref=backref('parent', remote_side=[categories.c.id]),
        order_by=categories.c.name.asc(),
        collection_class=CategoryList,
        join_depth=2),
})


# TODO: Remove this function or refactor into CategoryQuery.
#       It was copied over from the tags models and isn't really required here
def fetch_categories(cat_ids):
    categories = DBSession.query(Category).filter(Category.id.in_(cat_ids)).all()
    return categories
