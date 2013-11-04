# This file is a part of MediaDrop (http://www.mediadrop.net),
# Copyright 2009-2013 MediaDrop contributors
# For the exact contribution history, see the git revision log.
# The source code contained in this file is licensed under the GPLv3 or
# (at your option) any later version.
# See LICENSE.txt in the main project directory, for more information.

from pylons import request
from tw.forms import CheckBoxList
from tw.forms.validators import All, FancyValidator, Invalid, PlainText

from mediadrop.forms import ListForm, SubmitButton, TextField
from mediadrop.lib.i18n import N_, _
from mediadrop.model import DBSession
from mediadrop.model.auth import Group, Permission
from mediadrop.plugin import events


class UniqueGroupname(FancyValidator):
    def _to_python(self, value, state):
        id = request.environ['pylons.routes_dict']['id']

        query = DBSession.query(Group).filter_by(group_name=value)
        if id != 'new':
            query = query.filter(Group.group_id != id)

        if query.count() != 0:
            raise Invalid(_('Group name already exists'), value, state)
        return value

class GroupForm(ListForm):
    template = 'admin/box-form.html'
    id = 'group-form'
    css_class = 'form'
    submit_text = None
    show_children_errors = True
    
    event = events.Admin.GroupForm
    
    fields = [
        TextField('display_name', label_text=N_('Display Name'), validator=TextField.validator(not_empty=True), maxlength=255),
        TextField('group_name', label_text=N_('Groupname'), validator=All(PlainText(not_empty=True), UniqueGroupname()), maxlength=16),
        CheckBoxList('permissions', label_text=N_('Group Permissions'), 
            css_classes=['details_fieldset'],
            options=lambda: DBSession.query(Permission.permission_id, Permission.description).all()
        ),
        SubmitButton('save', default=N_('Save'), named_button=True, css_classes=['btn', 'btn-save', 'blue', 'f-rgt']),
        SubmitButton('delete', default=N_('Delete'), named_button=True, css_classes=['btn', 'btn-delete']),
    ]

