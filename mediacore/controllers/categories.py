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

from pylons import config, request, response, session, tmpl_context
from sqlalchemy import orm, sql

from mediacore.lib.base import BaseController
from mediacore.lib.decorators import expose, expose_xhr, paginate, validate
from mediacore.lib.helpers import get_featured_category, redirect, url_for
from mediacore.model import Category, Media, Podcast, fetch_row
from mediacore.model.meta import DBSession

import logging
log = logging.getLogger(__name__)

class CategoriesController(BaseController):
    """
    Categories Controller

    Handles the display of the category hierarchy, displaying the media
    associated with any given category and its descendants.

    """

    def __init__(self, *args, **kwargs):
        super(CategoriesController, self).__init__(*args, **kwargs)

        tmpl_context.categories = Category.query.order_by(Category.name)\
            .populated_tree()
        category_slug = request.environ['pylons.routes_dict'].get('slug', None)

        if category_slug:
            tmpl_context.category = fetch_row(Category, slug=category_slug)
            tmpl_context.breadcrumb = tmpl_context.category.ancestors()
            tmpl_context.breadcrumb.append(tmpl_context.category)

    @expose('categories/index.html')
    def index(self, slug=None, **kwargs):
        categories = Category.query.order_by(Category.name).populated_tree()
        media = Media.query.published()\
            .options(orm.undefer('comment_count_published'))

        if tmpl_context.category:
            media = media.in_category(tmpl_context.category)

        latest = media.order_by(Media.publish_on.desc())
        popular = media.order_by(Media.popularity_points.desc())

        featured = None
        featured_cat = get_featured_category()
        if featured_cat and featured_cat is not tmpl_context.category:
            featured = media.in_category(featured_cat).first()
        if not featured:
            featured = popular.first()

        latest = latest.exclude(featured)[:5]
        popular = popular.exclude(latest, featured)[:5]

        return dict(
            featured = featured,
            latest = latest,
            popular = popular,
        )

    @expose('categories/more.html')
    @paginate('media', items_per_page=20)
    def more(self, slug, order, page=1, **kwargs):
        media = Media.query.published()\
            .options(orm.undefer('comment_count_published'))\
            .in_category(tmpl_context.category)

        if order == 'latest':
            media = media.order_by(Media.publish_on.desc())
        else:
            media = media.order_by(Media.popularity_points.desc())

        return dict(
            media = media,
            order = order,
        )

