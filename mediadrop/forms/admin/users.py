# This file is a part of MediaDrop (http://www.mediadrop.net),
# Copyright 2009-2013 MediaDrop contributors
# For the exact contribution history, see the git revision log.
# The source code contained in this file is licensed under the GPLv3 or
# (at your option) any later version.
# See LICENSE.txt in the main project directory, for more information.

from pylons import request
from tw.forms import CheckBoxList, PasswordField
from tw.forms.validators import All, FancyValidator, FieldsMatch, Invalid, NotEmpty, PlainText, Schema

from mediadrop.forms import ListFieldSet, ListForm, SubmitButton, TextField, email_validator
from mediadrop.lib.i18n import N_, _
from mediadrop.model import DBSession
from mediadrop.model.auth import Group, User
from mediadrop.plugin import events


class UniqueUsername(FancyValidator):
    def _to_python(self, value, state):
        id = request.environ['pylons.routes_dict']['id']

        query = DBSession.query(User).filter_by(user_name=value)
        if id != 'new':
            query = query.filter(User.id != id)

        if query.count() != 0:
            raise Invalid(_('User name already exists'), value, state)
        return value

class UserForm(ListForm):
    template = 'admin/box-form.html'
    id = 'user-form'
    css_class = 'form'
    submit_text = None
    show_children_errors = True
    _name = 'user-form' # TODO: Figure out why this is required??
    
    event = events.Admin.UserForm
    
    fields = [
        TextField('display_name', label_text=N_('Display Name'), validator=TextField.validator(not_empty=True), maxlength=255),
        TextField('email_address', label_text=N_('Email Address'), validator=email_validator(not_empty=True), maxlength=255),
        ListFieldSet('login_details', suppress_label=True, legend=N_('Login Details:'),
            css_classes=['details_fieldset'],
            validator = Schema(chained_validators=[
                FieldsMatch('password', 'confirm_password',
                messages={'invalidNoMatch': N_("Passwords do not match"),})]
            ),
            children=[
                CheckBoxList('groups', label_text=N_('Groups'), 
                    options=lambda: Group.custom_groups(Group.group_id, Group.display_name).all()),
                TextField('user_name', label_text=N_('Username'), maxlength=16, validator=All(PlainText(), UniqueUsername(not_empty=True))),
                PasswordField('password', label_text=N_('Password'), validators=NotEmpty, maxlength=80, attrs={'autocomplete': 'off'}),
                PasswordField('confirm_password', label_text=N_('Confirm password'), validators=NotEmpty, maxlength=80, attrs={'autocomplete': 'off'}),
            ]
        ),
        SubmitButton('save', default=N_('Save'), named_button=True, css_classes=['btn', 'btn-save', 'blue', 'f-rgt']),
        SubmitButton('delete', default=N_('Delete'), named_button=True, css_classes=['btn', 'btn-delete']),
    ]
