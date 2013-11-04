# This file is a part of MediaDrop (http://www.mediadrop.net),
# Copyright 2009-2013 MediaDrop contributors
# For the exact contribution history, see the git revision log.
# The source code contained in this file is licensed under the GPLv3 or
# (at your option) any later version.
# See LICENSE.txt in the main project directory, for more information.

from pylons import request, tmpl_context

from mediadrop.forms.admin.groups import GroupForm
from mediadrop.lib.auth import has_permission
from mediadrop.lib.base import BaseController
from mediadrop.lib.decorators import (autocommit, expose, observable, paginate, validate)
from mediadrop.lib.helpers import redirect, url_for
from mediadrop.model import fetch_row, Group, Permission
from mediadrop.model.meta import DBSession
from mediadrop.plugin import events

group_form = GroupForm()


class GroupsController(BaseController):
    """Admin group actions"""
    allow_only = has_permission('admin')

    @expose('admin/groups/index.html')
    @paginate('groups', items_per_page=50)
    @observable(events.Admin.GroupsController.index)
    def index(self, page=1, **kwargs):
        """List groups with pagination.

        :param page: Page number, defaults to 1.
        :type page: int
        :rtype: Dict
        :returns:
            users
                The list of :class:`~mediadrop.model.auth.Group`
                instances for this page.

        """
        groups = DBSession.query(Group).order_by(Group.display_name, 
                                                 Group.group_name)
        return dict(groups=groups)


    @expose('admin/groups/edit.html')
    @observable(events.Admin.GroupsController.edit)
    def edit(self, id, **kwargs):
        """Display the :class:`~mediadrop.forms.admin.groups.GroupForm` for editing or adding.

        :param id: Group ID
        :type id: ``int`` or ``"new"``
        :rtype: dict
        :returns:
            user
                The :class:`~mediadrop.model.auth.Group` instance we're editing.
            user_form
                The :class:`~mediadrop.forms.admin.groups.GroupForm` instance.
            user_action
                ``str`` form submit url
            group_values
                ``dict`` form values

        """
        group = fetch_row(Group, id)

        if tmpl_context.action == 'save' or id == 'new':
            # Use the values from error_handler or GET for new groups
            group_values = kwargs
        else:
            permission_ids = map(lambda permission: permission.permission_id, group.permissions)
            group_values = dict(
                display_name = group.display_name,
                group_name = group.group_name,
                permissions = permission_ids
            )

        return dict(
            group = group,
            group_form = group_form,
            group_action = url_for(action='save'),
            group_values = group_values,
        )


    @expose(request_method='POST')
    @validate(group_form, error_handler=edit)
    @autocommit
    @observable(events.Admin.GroupsController.save)
    def save(self, id, display_name, group_name, permissions, delete=None, **kwargs):
        """Save changes or create a new :class:`~mediadrop.model.auth.Group` instance.

        :param id: Group ID. If ``"new"`` a new group is created.
        :type id: ``int`` or ``"new"``
        :returns: Redirect back to :meth:`index` after successful save.

        """
        group = fetch_row(Group, id)

        if delete:
            DBSession.delete(group)
            redirect(action='index', id=None)
        
        group.display_name = display_name
        group.group_name = group_name
        if permissions:
            query = DBSession.query(Permission).filter(Permission.permission_id.in_(permissions))
            group.permissions = list(query.all())
        else:
            group.permissions = []
        DBSession.add(group)

        redirect(action='index', id=None)


    @expose('json', request_method='POST')
    @autocommit
    @observable(events.Admin.GroupsController.delete)
    def delete(self, id, **kwargs):
        """Delete a group.

        :param id: Group ID.
        :type id: ``int``
        :returns: Redirect back to :meth:`index` after successful delete.
        """
        group = fetch_row(Group, id)
        DBSession.delete(group)

        if request.is_xhr:
            return dict(success=True)
        redirect(action='index', id=None)

