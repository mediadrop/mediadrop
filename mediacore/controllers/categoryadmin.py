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
from sqlalchemy import orm, sql
from repoze.what.predicates import has_permission

from mediacore.lib.base import (BaseController, url_for, redirect,
    expose, expose_xhr, validate, paginate)
from mediacore.lib import helpers
from mediacore.model import (DBSession, fetch_row, get_available_slug,
    Tag, Category)
from mediacore.forms.categories import EditCategoryForm


edit_form = EditCategoryForm()

class CategoryadminController(BaseController):
    allow_only = has_permission('admin')

    @expose_xhr('mediacore.templates.admin.categories.index',
                'mediacore.templates.admin.categories.index-table')
    @paginate('categories', items_per_page=25)
    def index(self, page=1, category='categories', **kwargs):
        """List categories or tags with pagination.

        :param category: ``categories`` or ``tags``
        :param page: Page number, defaults to 1.
        :type page: int
        :rtype: Dict
        :returns:
            categories
                The list of :class:`~mediacore.model.tags.Tag`
                or :class:`~mediacore.model.categories.Category`
                instances for this page.
            category
                ``categories`` or ``tags``
            category_name
                ``Categories`` or ``Tags``
            edit_form
                The :class:`~mediacore.forms.categories.EditCategoryForm` instance.

        """
        model = self.select_model(category)
        categories = DBSession.query(model)\
            .options(orm.undefer('media_count'))\
            .order_by(model.name)

        return dict(
            categories = categories,
            category = category,
            category_name = category.capitalize(),
            edit_form = edit_form,
        )


    @expose('json')
    @validate(edit_form)
    def save(self, id, delete, category='categories', **kwargs):
        """Save changes or create a category or tag.

        See :class:`~mediacore.forms.categories.EditCategoryForm` for POST vars.

        :param id: Category or tag ID
        :param category: ``categories`` or ``tags``
        :param delete: If true the category is deleted rather than saved.
        :type delete: bool
        :rtype: JSON dict
        :returns:
            success
                bool
            category
                ``categories`` or ``tags``

        """
        model = self.select_model(category)
        item = fetch_row(model, id)

        if delete:
            DBSession.delete(item)
            item = None
        else:
            item.name = kwargs['name']
            item.slug = get_available_slug(model, kwargs['slug'], item)

            DBSession.add(item)

        if request.is_xhr:
            return dict(success=True, category=item)
        else:
            redirect(action='index', category=category)


    def select_model(self, category):
        """Return the a category mapped class by the given name.

        :param category: ``categories`` or ``tags``
        :returns: A mapped class, :class:`~mediacore.model.categories.Category`
            or :class:`~mediacore.model.tags.Tag`
        :raises KeyError: If ``category`` is invalid.

        """
        return {
            'categories': Category,
            'tags': Tag,
        }.get(category)
