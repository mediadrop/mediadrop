from tg import expose, validate, flash, require, url, request
from tg.decorators import paginate
from formencode import validators
from pylons.i18n import ugettext as _
from sqlalchemy import and_, or_
from sqlalchemy.orm import eagerload
from repoze.what.predicates import has_permission

from mediaplex.lib import helpers
from mediaplex.lib.base import RoutingController
from mediaplex.lib.helpers import expose_xhr, redirect, url_for
from mediaplex import model
from mediaplex.model import DBSession, metadata, fetch_row, Tag, Topic, get_available_slug
from mediaplex.forms.categories import EditCategoryForm


class CategoryadminController(RoutingController):
    """Admin categories actions which deal with categories"""
    allow_only = has_permission('admin')

    @expose_xhr('mediaplex.templates.admin.categories.index',
                'mediaplex.templates.admin.categories.index-table')
    @paginate('categories', items_per_page=25)
    def index(self, page=1, category='topics', **kwargs):
        model = self.select_model(category)

        categories = DBSession.query(model).\
            order_by(model.name)

        return dict(
            categories = categories,
            category = category,
            category_name = category.capitalize(),
            edit_form = EditCategoryForm(),
        )

    @expose('json')
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
        return getattr(model, category.rstrip('s').capitalize())
