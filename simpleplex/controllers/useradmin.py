from tg import request
from tg.decorators import paginate, expose, validate
from repoze.what.predicates import has_permission
from pylons import tmpl_context

from simpleplex.lib.base import RoutingController
from simpleplex.lib.helpers import expose_xhr, redirect, url_for
from simpleplex.model import DBSession, fetch_row
from simpleplex.model.auth import User, Group, fetch_user, fetch_group
from simpleplex.forms.users import UserForm

from tg.exceptions import HTTPNotFound

user_form = UserForm()

class UseradminController(RoutingController):
    """Admin user actions"""
    allow_only = has_permission('admin')

    @expose_xhr('simpleplex.templates.admin.users.index',
                'simpleplex.templates.admin.users.index-table')
    @paginate('users', items_per_page=50)
    def index(self, page=1, **kwargs):
        users = DBSession.query(User)\
            .order_by(User.display_name)

        return dict(
            users = users,
            section = 'Users'
        )

    @expose('simpleplex.templates.admin.users.edit')
    def edit(self, id, **kwargs):
        """Display the edit form, or create a new one if the id is 'new'.

        This page serves as the error_handler for every kind of edit action,
        if anything goes wrong with them they'll be redirected here.
        """
        user = fetch_user(id)

        if tmpl_context.action == 'save' or id == 'new':
            # Use the values from error_handler or GET for new users
            user_values = kwargs
            user_values['password'] = None
        else:
            # Pull the defaults from the user item
            group = None
            if len(user.groups) == 1:
                group = user.groups[0].group_id

            user_values = dict(
                display_name = user.display_name,
                email_address = user.email_address,
                group = group,
                user_name = user.user_name,
            )

        if id != 'new':
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
    def save(self, id, email_address, display_name, group, user_name, password, delete=None, **kwargs):
        """Create or edit the metadata for a user item."""
        user = fetch_user(id)

        if delete:
            DBSession.delete(user)
            user = None
            redirect(action='index', id=None)

        user.display_name = display_name
        user.email_address = email_address
        user.user_name = user_name

        if group is not None:
            group = fetch_group(group)
            user.groups = [group,]

        if password is not None and password != '':
            user.password = password

        DBSession.add(user)
        DBSession.flush()

        redirect(action='index', id=None)

    @expose('json')
    def delete(self, id, **kwargs):
        """Delete a user item"""
        user = fetch_user(id)

        DBSession.delete(user)
        user = None

        if request.is_xhr:
            return dict(success=True)

        redirect(action='index', id=None)
