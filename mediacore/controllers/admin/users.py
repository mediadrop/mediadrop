# This file is a part of MediaDrop (http://www.mediadrop.net),
# Copyright 2009-2013 MediaDrop contributors
# For the exact contribution history, see the git revision log.
# The source code contained in this file is licensed under the GPLv3 or
# (at your option) any later version.
# See LICENSE.txt in the main project directory, for more information.

from pylons import request, tmpl_context
import webob.exc

from mediacore.forms.admin.users import UserForm
from mediacore.lib.auth import has_permission
from mediacore.lib.base import BaseController
from mediacore.lib.decorators import (autocommit, expose, expose_xhr,
    observable, paginate, validate)
from mediacore.lib.helpers import redirect, url_for
from mediacore.model import Group, User, fetch_row
from mediacore.model.meta import DBSession
from mediacore.plugin import events

user_form = UserForm()


class UsersController(BaseController):
    """Admin user actions"""
    allow_only = has_permission('admin')

    @expose_xhr('admin/users/index.html')
    @paginate('users', items_per_page=50)
    @observable(events.Admin.UsersController.index)
    def index(self, page=1, **kwargs):
        """List users with pagination.

        :param page: Page number, defaults to 1.
        :type page: int
        :rtype: Dict
        :returns:
            users
                The list of :class:`~mediacore.model.auth.User`
                instances for this page.

        """
        users = DBSession.query(User).order_by(User.display_name,
                                               User.email_address)
        return dict(users=users)


    @expose('admin/users/edit.html')
    @observable(events.Admin.UsersController.edit)
    def edit(self, id, **kwargs):
        """Display the :class:`~mediacore.forms.admin.users.UserForm` for editing or adding.

        :param id: User ID
        :type id: ``int`` or ``"new"``
        :rtype: dict
        :returns:
            user
                The :class:`~mediacore.model.auth.User` instance we're editing.
            user_form
                The :class:`~mediacore.forms.admin.users.UserForm` instance.
            user_action
                ``str`` form submit url
            user_values
                ``dict`` form values

        """
        user = fetch_row(User, id)

        if tmpl_context.action == 'save' or id == 'new':
            # Use the values from error_handler or GET for new users
            user_values = kwargs
            user_values['login_details.password'] = None
            user_values['login_details.confirm_password'] = None
        else:
            group_ids = None
            if user.groups:
                group_ids = map(lambda group: group.group_id, user.groups)
            user_values = dict(
                display_name = user.display_name,
                email_address = user.email_address,
                login_details = dict(
                    groups = group_ids,
                    user_name = user.user_name,
                ),
            )

        return dict(
            user = user,
            user_form = user_form,
            user_action = url_for(action='save'),
            user_values = user_values,
        )


    @expose(request_method='POST')
    @validate(user_form, error_handler=edit)
    @autocommit
    @observable(events.Admin.UsersController.save)
    def save(self, id, email_address, display_name, login_details,
             delete=None, **kwargs):
        """Save changes or create a new :class:`~mediacore.model.auth.User` instance.

        :param id: User ID. If ``"new"`` a new user is created.
        :type id: ``int`` or ``"new"``
        :returns: Redirect back to :meth:`index` after successful save.

        """
        user = fetch_row(User, id)

        if delete:
            DBSession.delete(user)
            redirect(action='index', id=None)

        user.display_name = display_name
        user.email_address = email_address
        user.user_name = login_details['user_name']

        password = login_details['password']
        if password is not None and password != '':
            user.password = password

        if login_details['groups']:
            query = DBSession.query(Group).filter(Group.group_id.in_(login_details['groups']))
            user.groups = list(query.all())
        else:
            user.groups = []

        DBSession.add(user)

        # Check if we're changing the logged in user's own password
        if user.id == request.perm.user.id \
        and password is not None and password != '':
            DBSession.commit()
            # repoze.who sees the Unauthorized response and clears the cookie,
            # forcing a fresh login with the new password
            raise webob.exc.HTTPUnauthorized().exception

        redirect(action='index', id=None)


    @expose('json', request_method='POST')
    @autocommit
    @observable(events.Admin.UsersController.delete)
    def delete(self, id, **kwargs):
        """Delete a user.

        :param id: User ID.
        :type id: ``int``
        :returns: Redirect back to :meth:`index` after successful delete.
        """
        user = fetch_row(User, id)
        DBSession.delete(user)

        if request.is_xhr:
            return dict(success=True)
        redirect(action='index', id=None)
