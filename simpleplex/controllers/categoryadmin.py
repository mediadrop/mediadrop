from tg import expose, validate, require, request
from repoze.what.predicates import has_permission

from simpleplex.lib import helpers
from simpleplex.lib.base import RoutingController
from simpleplex.lib.helpers import expose_xhr, paginate, redirect, url_for
from simpleplex import model
from simpleplex.model import DBSession, metadata, fetch_row, Tag, Topic, get_available_slug
from simpleplex.forms.categories import EditCategoryForm

edit_category_form = EditCategoryForm()

class CategoryadminController(RoutingController):
    """Admin categories actions which deal with categories"""
    allow_only = has_permission('admin')

    @expose_xhr('simpleplex.templates.admin.categories.index',
                'simpleplex.templates.admin.categories.index-table')
    @paginate('categories', items_per_page=25)
    def index(self, page=1, category='topics', **kwargs):
        model = self.select_model(category)

        categories = DBSession.query(model).\
            order_by(model.name)

        return dict(
            categories = categories,
            category = category,
            category_name = category.capitalize(),
            edit_form = edit_category_form,
            section = category.capitalize()
        )

    @expose('json')
    @validate(edit_category_form)
    def save(self, id, delete, category='topics', **kwargs):
        model_class = self.select_model(category)
        item = fetch_row(model_class, id)

        if delete:
            DBSession.delete(item)
            item = None
        else:
            if item.id == 'new':
                item.id = None

            item.name = kwargs['name']
            item.slug = get_available_slug(model_class, kwargs['slug'], item)

            DBSession.add(item)

        if request.is_xhr:
            return dict(success=True, category=item)
        else:
            redirect(action='index', category=category)

    def select_model(self, category):
        return {'topics': Topic, 'tags': Tag}.get(category)
