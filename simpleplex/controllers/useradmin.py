from tg.decorators import paginate, expose, validate
from repoze.what.predicates import has_permission
from pylons import tmpl_context

from simpleplex.lib.base import RoutingController
from simpleplex.lib.helpers import expose_xhr, redirect, url_for
from simpleplex.model import DBSession
from simpleplex.model.auth import User, fetch_user
from simpleplex.forms.users import UserForm

user_form = UserForm()

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

    @expose('simpleplex.templates.admin.users.edit')
    def edit(self, user_id, **kwargs):
        """Display the edit form, or create a new one if the user_id is 'new'.

        This page serves as the error_handler for every kind of edit action,
        if anything goes wrong with them they'll be redirected here.
        """
        user = fetch_user(user_id)

        if tmpl_context.action == 'save' or user_id == 'new':
            # Use the values from error_handler or GET for new users
            user_values = kwargs
            user_values['password'] = None
        else:
            # Pull the defaults from the user item
            user_values = dict(
                user_name = user.user_name,
                display_name = user.display_name,
                email_address = user.email_address,
            )

        if user_id != 'new':
            DBSession.add(user)

        return dict(
            user = user,
            user_form = user_form,
            user_action = url_for(action='save'),
            user_values = user_values,
            section = 'Users'
        )

    @expose()
    @validate(user_form, error_handler=edit)
    def save(self, user_id, user_name, display_name, email_address, password, delete=None, **kwargs):
        """Create or edit the metadata for a user item."""
        user = fetch_user(user_id)

        if delete:
            DBSession.delete(user)
            user = None
            redirect(action='index', user_id=None)

        user.user_name = user_name
        user.display_name = display_name
        user.email_address = email_address
        if(password is not None and password != ''):
            user.password = password

        DBSession.add(user)
        DBSession.flush()

        redirect(action='index', user_id=None)
