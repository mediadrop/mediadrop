# This file is a part of MediaCore CE, Copyright 2009-2012 MediaCore Inc.
# The source code contained in this file is licensed under the GPL.
# See LICENSE.txt in the main project directory, for more information.

from pylons import request
from tw.forms import PasswordField, SingleSelectField
from tw.forms.validators import All, FancyValidator, FieldsMatch, Invalid, NotEmpty, PlainText, Schema

from mediacore.forms import ListFieldSet, ListForm, SubmitButton, TextField, email_validator
from mediacore.lib.i18n import N_, _
from mediacore.model import DBSession
from mediacore.model.auth import Group, User
from mediacore.plugin import events


class UniqueUsername(FancyValidator):
    def _to_python(self, value, state):
        id = request.environ['pylons.routes_dict']['id']

        query = DBSession.query(User).filter_by(user_name=value)
        if id != 'new':
            query = query.filter(User.user_id != id)

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

    fields = [
        TextField('display_name', label_text=N_('Display Name'), validator=TextField.validator(not_empty=True), maxlength=255),
        TextField('email_address', label_text=N_('Email Address'), validator=email_validator(not_empty=True), maxlength=255),
        ListFieldSet('login_details', suppress_label=True, legend=N_('Login Details:'),
                     css_classes=['details_fieldset'],
                     validator = Schema(chained_validators=[FieldsMatch('password',
                                                                        'confirm_password',
                                                                        messages={'invalidNoMatch': N_("Passwords do not match"),})]),
                     children=[
            SingleSelectField('group', label_text=N_('Group'),
                options=lambda: DBSession.query(Group.group_id, Group.display_name).all()),
            TextField('user_name', label_text=N_('Username'), maxlength=16, validator=All(PlainText(), UniqueUsername(not_empty=True))),
            PasswordField('password', label_text=N_('Password'), validators=NotEmpty, maxlength=80, autocomplete='off'),
            PasswordField('confirm_password', label_text=N_('Confirm password'), validators=NotEmpty, maxlength=80),
        ]),
        SubmitButton('save', default=N_('Save'), named_button=True, css_classes=['btn', 'btn-save', 'blue', 'f-rgt']),
        SubmitButton('delete', default=N_('Delete'), named_button=True, css_classes=['btn', 'btn-delete']),
    ]

    def post_init(self, *args, **kwargs):
        events.Admin.UserForm(self)
