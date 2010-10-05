# This file is a part of MediaCore, Copyright 2009 Simple Station Inc.
#
# MediaCore is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# MediaCore is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from pylons import request
from pylons.i18n import N_ as _
from tw.forms import PasswordField, SingleSelectField
from tw.forms.validators import All, FancyValidator, FieldsMatch, Invalid, NotEmpty, PlainText, Schema

from mediacore.forms import ListFieldSet, ListForm, SubmitButton, TextField, email_validator
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
        TextField('display_name', label_text=_('Display Name'), validator=TextField.validator(not_empty=True), maxlength=255),
        TextField('email_address', label_text=_('Email Address'), validator=email_validator(not_empty=True), maxlength=255),
        ListFieldSet('login_details', suppress_label=True, legend=_('Login Details:'),
                     css_classes=['details_fieldset'],
                     validator = Schema(chained_validators=[FieldsMatch('password',
                                                                        'confirm_password',
                                                                        messages={'invalidNoMatch': _("Passwords do not match"),})]),
                     children=[
            SingleSelectField('group', label_text=_('Group'),
                options=lambda: DBSession.query(Group.group_id, Group.display_name).all()),
            TextField('user_name', label_text=_('Username'), maxlength=16, validator=All(PlainText(), UniqueUsername(not_empty=True))),
            PasswordField('password', label_text=_('Password'), validators=NotEmpty, maxlength=80, autocomplete='off'),
            PasswordField('confirm_password', label_text=_('Confirm password'), validators=NotEmpty, maxlength=80),
        ]),
        SubmitButton('save', default=_('Save'), named_button=True, css_classes=['btn', 'btn-save', 'f-rgt']),
        SubmitButton('delete', default=_('Delete'), named_button=True, css_classes=['btn', 'btn-delete']),
    ]

    def post_init(self, *args, **kwargs):
        events.Admin.UserForm(self)
