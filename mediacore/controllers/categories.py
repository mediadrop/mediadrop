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

from tg import config, request, response, tmpl_context
from sqlalchemy import orm
from repoze.what.predicates import has_permission
from paste.util import mimeparse
import pylons.templating

from mediacore.lib.base import (BaseController, url_for, redirect,
    expose, expose_xhr, validate, paginate)
from mediacore.model import (DBSession, fetch_row,
    Podcast, Media, Category)


class CategoriesController(BaseController):
    @expose('mediacore.templates.categories.index')
    @paginate('media', items_per_page=12, items_first_page=11)
    def index(self, slug=None, page=1, **kwargs):
        categories = Category.query.populated_tree()
        media = Media.query.published()\
            .order_by(Media.publish_on.desc())\
            .options(orm.undefer('comment_count_published'))

        if slug:
            category = fetch_row(Category, slug=slug)
            media = media.in_category(category)
            breadcrumb = category.ancestors()
            breadcrumb.append(category)
        else:
            category = None
            breadcrumb = []

        return dict(
            categories = categories,
            media = media,
            category = category,
            breadcrumb = breadcrumb,
        )
