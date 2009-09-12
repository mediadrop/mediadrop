from tg.decorators import paginate
from repoze.what.predicates import has_permission

from simpleplex.lib.base import RoutingController
from simpleplex.lib.helpers import expose_xhr, redirect, url_for
from simpleplex.model import DBSession, User


class UseradminController(RoutingController):
    """Admin user actions"""
    allow_only = has_permission('admin')

    @expose_xhr('simpleplex.templates.admin.users.index',
                'simpleplex.templates.admin.users.index-table')
    @paginate('users', items_per_page=50)
    def index(self, page=1, **kwargs):
        users = DBSession.query(User)\
            .order_by(User.user_name)

        return dict(
            users = users,
            section = 'Users'
        )

