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

from tg import config, request, response, tmpl_context as c
from sqlalchemy import orm, sql

from mediacore.lib.base import (BaseController, url_for, redirect,
    expose, expose_xhr, validate, paginate)
from mediacore.model import (DBSession, fetch_row,
    Podcast, Media, Category)


class CategoriesController(BaseController):
    """
    Categories Controller

    Handles the display of the category hierarchy, displaying the media
    associated with any given category and its descendants.

    """

    def __init__(self, *args, **kwargs):
        super(CategoriesController, self).__init__(*args, **kwargs)

        c.categories = Category.query.order_by(Category.name)\
            .populated_tree()
        category_slug = request.environ['pylons.routes_dict'].get('slug', None)

        if category_slug:
            c.category = fetch_row(Category, slug=category_slug)
            c.breadcrumb = c.category.ancestors()
            c.breadcrumb.append(c.category)

    @expose('mediacore.templates.categories.index')
    def index(self, slug=None, **kwargs):
        categories = Category.query.order_by(Category.name).populated_tree()
        media = Media.query.published()\
            .options(orm.undefer('comment_count_published'))

        if c.category:
            media = media.in_category(c.category)

        latest = media.order_by(Media.publish_on.desc())[:5]
        popular = media.order_by(Media.popularity_points.desc())\
            .filter(sql.not_(Media.id.in_([m.id for m in latest])))[:5]

        return dict(
            latest = latest,
            popular = popular,
        )

    @expose('mediacore.templates.categories.more')
    @paginate('media', items_per_page=20)
    def more(self, slug, order, page=1, **kwargs):
        media = Media.query.published()\
            .options(orm.undefer('comment_count_published'))\
            .in_category(c.category)

        if order == 'latest':
            media = media.order_by(Media.publish_on.desc())
        else:
            media = media.order_by(Media.popularity_points.desc())

        return dict(
            media = media,
            order = order,
        )
