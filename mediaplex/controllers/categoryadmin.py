from tg import expose, validate, flash, require, url, request
from tg.decorators import paginate
from formencode import validators
from pylons.i18n import ugettext as _
from sqlalchemy import and_, or_
from sqlalchemy.orm import eagerload
from repoze.what.predicates import has_permission

from mediaplex.lib import helpers
from mediaplex.lib.base import RoutingController
from mediaplex.lib.helpers import expose_xhr, redirect, url_for, strip_xhtml, slugify
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
    def delete(self, category, id, **kwargs):
        # FIXME: This method used to return absolutely nothing.
        # Our convention is to return JSON with a 'success' value for all ajax actions.
        # The JS needs to be updated to check for this value.
        category = fetch_row(self.select_model(category), id)
        DBSession.delete(category)
        return dict(success=True)

    @expose('json')
    def save(self, id, category='topics', **kwargs):
        model_class = self.select_model(category)
        category = fetch_row(model_class, id)

        if category.id == 'new':
            category.id = None

        category.name = strip_xhtml(kwargs['name'])
        category.slug = get_available_slug(model_class, slugify(strip_xhtml(kwargs['slug'])))

        DBSession.add(category)
        return dict(success=True,category=category)

    def select_model(self, category):
        return getattr(model, category.rstrip('s').capitalize())
