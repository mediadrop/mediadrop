from tw.forms.validators import NotEmpty, Email
import formencode
from tg import request

from simpleplex.forms import Form, ListForm, ListFieldSet, TextField, XHTMLTextArea, FileField, CalendarDatePicker, SingleSelectField, TextArea, SubmitButton, Button, HiddenField, CheckBoxList, PasswordField

from simpleplex.model import DBSession
from simpleplex.model.auth import Group, User

class UniqueUsername(formencode.FancyValidator):
    def _to_python(self, value, state):
        user_id = request.environ['pylons.routes_dict']['user_id']

        query = DBSession.query(User).filter_by(user_name=value)
        if user_id != 'new':
            query = query.filter(User.user_id != user_id)

        if query.count() != 0:
            raise formencode.Invalid(
                'User name already exists',
                value, state)
        return value

class UserForm(ListForm):
    template = 'simpleplex.templates.admin.box-form'
    id = 'user-form'
    css_class = 'form'
    submit_text = None
    show_children_errors = True
    _name = 'user-form' # TODO: Figure out why this is required??

    fields = [
        TextField('display_name', validator=NotEmpty, maxlength=255),
        TextField('email_address', validator=Email(not_empty=True, messages={
            'badUsername': 'The portion of the email address before the @ is invalid',
            'badDomain': 'The portion of this email address after the @ is invalid'
        }), maxlength=255),
        ListFieldSet('login_details', suppress_label=True, legend='Login Details:', css_classes=['details_fieldset'], children=[
            SingleSelectField('group', label_text='Group', options=lambda: DBSession.query(Group.group_id, Group.display_name).all()),
            TextField('user_name', maxlength=16, validator=UniqueUsername(not_empty=True)),
            PasswordField('password', validators=NotEmpty),
            PasswordField('confirm_password', validators=NotEmpty, maxlength=80),
        ]),
        SubmitButton('save', default='Save', named_button=True, css_classes=['mo', 'btn-save', 'f-rgt']),
        SubmitButton('delete', default='Delete', named_button=True, css_classes=['mo', 'btn-delete']),
    ]
