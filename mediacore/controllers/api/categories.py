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

import logging
from datetime import datetime, timedelta

from paste.util.converters import asbool
from pylons import config
from sqlalchemy import orm

from mediacore.controllers.api import APIException, get_order_by
from mediacore.lib import helpers
from mediacore.lib.base import BaseController
from mediacore.lib.decorators import expose
from mediacore.lib.helpers import get_featured_category, url_for
from mediacore.lib.thumbnails import thumb
from mediacore.model import Category
from mediacore.model.meta import DBSession

log = logging.getLogger(__name__)

order_columns = {
    'id': Category.id,
    'name': Category.name,
    'slug': Category.slug,
}

class CategoryController(BaseController):
    """
    JSON Category API
    """

    @expose('json')
    def index(self, order=None, offset=0, limit=10, **kwargs):
        """Query for a flat list of categories.

        :param id: A :attr:`mediacore.model.media.Category.id` for lookup
        :type id: int

        :param name: A :attr:`mediacore.model.media.Category.name` for lookup

        :param slug: A :attr:`mediacore.model.media.Category.slug` for lookup
        :type slug: str

        :param order:
            A column name and 'asc' or 'desc', seperated by a space.
            The column name can be any one of the returned columns.
            Defaults to newest category first (id desc).

        :param offset:
            Where in the complete resultset to start returning results.
            Defaults to 0, the very beginning. This is useful if you've
            already fetched the first 50 results and want to fetch the
            next 50 and so on.
        :type offset: int

        :param limit:
            Number of results to return in each query. Defaults to 10.
            The maximum allowed value defaults to 50 and is set via
            :attr:`mediacore.config['app_config'].api_media_max_results`.
        :type limit: int

        :returns: JSON dict

        """

        if True in [(key in kwargs) for key in ('id', 'slug', 'name')]:
            kwargs['offset'] = offset
            kwargs['limit'] = limit
            kwargs['tree'] = False
            return self._get_query(**kwargs)

        return self._index_query(order, offset, limit, tree=False, parents=False)

    @expose('json')
    def parents(self, order=None, offset=0, limit=10, **kwargs):
        """Query for a flat list of parent categories

         :param order:
            A column name and 'asc' or 'desc', seperated by a space.
            The column name can be any one of the returned columns.
            Defaults to newest category first (id desc).

        :param offset:
            Where in the complete resultset to start returning results.
            Defaults to 0, the very beginning. This is useful if you've
            already fetched the first 50 results and want to fetch the
            next 50 and so on.
        :type offset: int

        :param limit:
            Number of results to return in each query. Defaults to 10.
            The maximum allowed value defaults to 50 and is set via
            :attr:`mediacore.config['app_config'].api_media_max_results`.
        :type limit: int

        :returns: JSON dict

        """
        return self._index_query(order, offset, limit, tree=False, parents=True)

    @expose('json')
    def tree(self, depth=10, **kwargs):
        """Query for an expanded tree of categories.

        :param id: A :attr:`mediacore.model.media.Category.id` to lookup the parent node
        :type id: int
        :param name: A :attr:`mediacore.model.media.Category.name` to lookup the parent node
        :param slug: A :attr:`mediacore.model.media.Category.slug` to lookup the parent node
        :type slug: str

        :param depth:
            Number of level deep in children to expand. Defaults to 10.
            The maximum allowed value defaults to 10 and is set via
            :attr:`mediacore.config['app_config'].api_tree_max_depth`.
        :type limit: int

        :returns: JSON dict

        """
        if True in [(key in kwargs) for key in ('id', 'slug', 'name')]:
            kwargs['depth'] = depth
            kwargs['tree'] = True
            return self._get_query(**kwargs)

        return self._index_query(depth=depth, tree=True)


    def _index_query(self, order=None, offset=0, limit=10, tree=False,
                     depth=10, parents=False, **kwargs):
        """Expose info on a specific category item by ID, name or slug.

        :param order:
            A column name and 'asc' or 'desc', seperated by a space.
            The column name can be any one of the returned columns.
            Defaults to newest category first (id desc).

        :param offset:
            Where in the complete resultset to start returning results.
            Defaults to 0, the very beginning. This is useful if you've
            already fetched the first 50 results and want to fetch the
            next 50 and so on.
        :type offset: int

        :param limit:
            Number of results to return in each query. Defaults to 10.
            The maximum allowed value defaults to 50 and is set via
            :attr:`mediacore.config['app_config'].api_media_max_results`.
        :type limit: int

        :param tree:
            If True Expand children objects. Defaults to False

        :param depth:
            The max levels deep to expand children

        :param parents:
            If True return only parent categories

        """
        if asbool(parents) or asbool(tree):
            query = Category.query.roots()
        else:
            query = Category.query

        if not order:
            order = 'id asc'

        query = query.order_by(get_order_by(order, order_columns))

        start = int(offset)
        limit = min(int(limit), int(config['api_media_max_results']))

        # get the total of all the matches
        count = query.count()

        query = query.offset(start).limit(limit)

        categories = self.expand(query.all(), asbool(tree), depth)

        return dict(
           categories = categories,
           count = count,
        )

    def _get_query(self, id=None, name=None, slug=None, tree=False, depth=10, **kwargs):
        """Query fora specific category item by ID, name or slug.

        :param id: A :attr:`mediacore.model.media.Category.id` for lookup
        :type id: int
        :param name: A :attr:`mediacore.model.media.Category.name` for lookup
        :param slug: A :attr:`mediacore.model.media.Category.slug` for lookup
        :type slug: str

        :param tree:
            If True Expand children objects. Defaults to False

        :param depth:
            The max levels deep to expand children

        """
        query = Category.query

        if id:
            query = query.filter_by(id=id)
        elif name:
            query = query.filter_by(name=name)
        else:
            query = query.filter_by(slug=slug)

        try:
            category = query.one()
        except (orm.exc.NoResultFound, orm.exc.MultipleResultsFound):
            return dict(error='No Match found')

        return dict(category=self.expand(category, tree, depth=depth))

    def expand(self, obj, children=False, depth=0):
        """Expand a category object into json."""
        depth = min(int(depth), int(config['api_tree_max_depth']))

        if isinstance(obj, Category):
            data = self._info(obj)
        if isinstance(obj, list):
            data = [self.expand(x, children, depth - 1) for x in obj]
        if isinstance(obj, dict):
            data = dict([(key, self.expand(value, children, depth - 1)) for key, value in obj])

        if children is True and depth > 0 and hasattr(obj, 'children') and len(obj.children):
            data['children'] = [self.expand(x, children) for x in obj.children]

        return data


    def _info(self, cat):
        """Return a JSON-ready dict for the given category instance."""
        data = dict(
            id = cat.id,
            name = cat.name,
            slug = cat.slug,
            media_count = cat.media_count_published,
        )
        if cat.parent:
            data['parent'] = cat.parent.name
        return data
