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

from datetime import datetime
from sqlalchemy import Table, ForeignKey, Column, sql
from sqlalchemy.types import String, Unicode, UnicodeText, Integer, DateTime, Boolean, Float
from sqlalchemy.orm import mapper, relation, backref, synonym, interfaces, validates, Query

from mediacore.model import metadata, DBSession, slugify


categories = Table('categories', metadata,
    Column('id', Integer, autoincrement=True, primary_key=True),
    Column('name', Unicode(50), unique=True, nullable=False),
    Column('slug', String(50), unique=True, nullable=False),
    Column('parent_id', Integer, ForeignKey('categories.id', onupdate='CASCADE', ondelete='CASCADE')),
    mysql_engine='InnoDB',
    mysql_charset='utf8'
)

def traverse(cats, depth=1):
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

    def roots(self):
        return self.filter(Category.parent_id == None)

    def all(self):
       return CategoryList(self)

class CategoryList(list):
    traverse = traverse

    def __unicode__(self):
        return ', '.join(cat.name for cat in self.itervalues())

class Category(object):
    """
    Category definition
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

    def find_depth(self):
        depth = 0
        ancestor = self.parent_id
        while ancestor:
            depth += 1
            ancestor = DBSession.execute(sql.select(
                [categories.c.parent_id],
                categories.c.id == ancestor
            )).scalar()
        return depth

    def has_ancestor(self, cat):
        cat = isinstance(cat, Category) and cat.id or int(cat)
        ancestor = self.parent_id
        while ancestor:
            if ancestor == cat:
                return True
            ancestor = DBSession.execute(sql.select(
                [categories.c.parent_id],
                categories.c.id == ancestor
            )).scalar()
        return False



mapper(Category, categories, properties={
    'children': relation(Category,
        backref=backref('parent', remote_side=[categories.c.id]),
        order_by=categories.c.name.asc(),
        collection_class=CategoryList,
        join_depth=3),
})


# TODO: Remove this function or refactor into CategoryQuery.
#       It was copied over from the tags models and isn't really required here
def fetch_categories(cat_ids):
    categories = DBSession.query(Category).filter(Category.id.in_(cat_ids)).all()
    return categories
