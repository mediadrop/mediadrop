# This file is a part of MediaDrop (http://www.mediadrop.net),
# Copyright 2009-2013 MediaDrop contributors
# For the exact contribution history, see the git revision log.
# The source code contained in this file is licensed under the GPLv3 or
# (at your option) any later version.
# See LICENSE.txt in the main project directory, for more information.

from pylons import request, tmpl_context
from sqlalchemy import orm

from mediacore.forms.admin.categories import CategoryForm, CategoryRowForm
from mediacore.lib.auth import has_permission
from mediacore.lib.base import BaseController
from mediacore.lib.decorators import (autocommit, expose, observable, paginate, 
    validate)
from mediacore.lib.helpers import redirect, url_for
from mediacore.model import Category, fetch_row, get_available_slug
from mediacore.model.meta import DBSession
from mediacore.plugin import events

import logging
log = logging.getLogger(__name__)

category_form = CategoryForm()
category_row_form = CategoryRowForm()

class CategoriesController(BaseController):
    allow_only = has_permission('edit')

    @expose('admin/categories/index.html')
    @paginate('tags', items_per_page=25)
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

    @expose('json', request_method='POST')
    @validate(category_form)
    @autocommit
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

    @expose('json', request_method='POST')
    @autocommit
    @observable(events.Admin.CategoriesController.bulk)
    def bulk(self, type=None, ids=None, **kwargs):
        """Perform bulk operations on media items

        :param type: The type of bulk action to perform (delete)
        :param ids: A list of IDs.

        """
        if not ids:
            ids = []
        elif not isinstance(ids, list):
            ids = [ids]


        if type == 'delete':
            Category.query.filter(Category.id.in_(ids)).delete(False)
            DBSession.commit()
            success = True
        else:
            success = False

        return dict(
            success = success,
            ids = ids,
            parent_options = unicode(category_form.c['parent_id'].display()),
        )
