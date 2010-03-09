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
from sqlalchemy import Table, ForeignKey, Column
from sqlalchemy.types import String, Unicode, UnicodeText, Integer, DateTime, Boolean, Float
from sqlalchemy.orm import mapper, relation, backref, synonym, interfaces, validates, Query

from mediacore.model import metadata, DBSession, slugify, _mtm_count_property


categories = Table('categories', metadata,
    Column('id', Integer, autoincrement=True, primary_key=True),
    Column('name', Unicode(50), unique=True, nullable=False),
    Column('slug', String(50), unique=True, nullable=False),
    Column('parent_id', Integer, ForeignKey('categories.id', onupdate='CASCADE', ondelete='CASCADE')),
    mysql_engine='InnoDB',
    mysql_charset='utf8'
)


class CategoryQuery(Query):
    pass

class Category(object):
    """
    Category definition
    """
    query = DBSession.query_property()

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

class CategoryList(list):
    def __unicode__(self):
        return ', '.join(cat.name for cat in self.itervalues())


mapper(Category, categories, properties={
    'children': relation(Category, backref=backref('parent', remote_side=[categories.c.id])),
})


# TODO: Remove this function or refactor into CategoryQuery.
#       It was copied over from the tags models and isn't really required here
def fetch_categories(cat_ids):
    categories = DBSession.query(Category).filter(Category.id.in_(cat_ids)).all()
    return categories
