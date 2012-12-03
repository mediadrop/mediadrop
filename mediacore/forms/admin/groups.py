# This file is a part of MediaCore CE, Copyright 2009-2012 MediaCore Inc.
# The source code contained in this file is licensed under the GPL.
# See LICENSE.txt in the main project directory, for more information.

from pylons import request
from tw.forms.validators import All, FancyValidator, Invalid, PlainText

from mediacore.forms import ListForm, SubmitButton, TextField
from mediacore.lib.i18n import N_, _
from mediacore.model import DBSession
from mediacore.model.auth import Group
from mediacore.plugin import events


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
        SubmitButton('save', default=N_('Save'), named_button=True, css_classes=['btn', 'btn-save', 'blue', 'f-rgt']),
        SubmitButton('delete', default=N_('Delete'), named_button=True, css_classes=['btn', 'btn-delete']),
    ]

