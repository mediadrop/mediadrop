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

from pylons import request, response, session, tmpl_context
from repoze.what.predicates import has_permission
from sqlalchemy import orm, sql

from mediacore.lib.base import BaseController
from mediacore.lib.decorators import expose, expose_xhr, observable, paginate, validate
from mediacore.lib.helpers import redirect, url_for
from mediacore.model import Category, fetch_row, get_available_slug
from mediacore.model.meta import DBSession
from mediacore.plugin import events

from mediacore.forms.admin.categories import CategoryForm, CategoryRowForm

import logging
log = logging.getLogger(__name__)

category_form = CategoryForm()
category_row_form = CategoryRowForm()

class CategoriesController(BaseController):
    allow_only = has_permission('edit')

    @expose('admin/categories/index.html')
    @observable(events.Admin.CategoriesController.index)
    def index(self, **kwargs):
        """List categories.

        :rtype: Dict
        :returns:
            categories
                The list of :class:`~mediacore.model.categories.Category`
                instances for this page.
            category_form
                The :class:`~mediacore.forms.admin.settings.categories.CategoryForm` instance.

        """
        categories = Category.query\
            .order_by(Category.name)\
            .options(orm.undefer('media_count'))\
            .populated_tree()

        return dict(
            categories = categories,
            category_form = category_form,
            category_row_form = category_row_form,
        )

    @expose('admin/categories/edit.html')
    @observable(events.Admin.CategoriesController.edit)
    def edit(self, id, **kwargs):
        """Edit a single category.

        :param id: Category ID
        :rtype: Dict
        :returns:
            categories
                The list of :class:`~mediacore.model.categories.Category`
                instances for this page.
            category_form
                The :class:`~mediacore.forms.admin.settings.categories.CategoryForm` instance.

        """
        category = fetch_row(Category, id)

        return dict(
            category = category,
            category_form = category_form,
            category_row_form = category_row_form,
        )

    @expose('json')
    @validate(category_form)
    @observable(events.Admin.CategoriesController.save)
    def save(self, id, delete=None, **kwargs):
        """Save changes or create a category.

        See :class:`~mediacore.forms.admin.settings.categories.CategoryForm` for POST vars.

        :param id: Category ID
        :param delete: If true the category is to be deleted rather than saved.
        :type delete: bool
        :rtype: JSON dict
        :returns:
            success
                bool

        """
        if tmpl_context.form_errors:
            if request.is_xhr:
                return dict(success=False, errors=tmpl_context.form_errors)
            else:
                # TODO: Add error reporting for users with JS disabled?
                return redirect(action='edit')

        cat = fetch_row(Category, id)

        if delete:
            DBSession.delete(cat)
            data = dict(
                success = True,
                id = cat.id,
                parent_options = unicode(category_form.c['parent_id'].display()),
            )
        else:
            cat.name = kwargs['name']
            cat.slug = get_available_slug(Category, kwargs['slug'], cat)

            if kwargs['parent_id']:
                parent = fetch_row(Category, kwargs['parent_id'])
                if parent is not cat and cat not in parent.ancestors():
                    cat.parent = parent
            else:
                cat.parent = None

            DBSession.add(cat)
            DBSession.flush()

            data = dict(
                success = True,
                id = cat.id,
                name = cat.name,
                slug = cat.slug,
                parent_id = cat.parent_id,
                parent_options = unicode(category_form.c['parent_id'].display()),
                depth = cat.depth(),
                row = unicode(category_row_form.display(
                    action = url_for(id=cat.id),
                    category = cat,
                    depth = cat.depth(),
                    first_child = True,
                )),
            )

        if request.is_xhr:
            return data
        else:
            redirect(action='index', id=None)
