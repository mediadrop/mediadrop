from tw.forms.validators import Invalid, NotEmpty, Email, Schema, FancyValidator, All, PlainText, FieldsMatch
from tg import request

from mediacore.forms import Form, ListForm, ListFieldSet, TextField, XHTMLTextArea, FileField, CalendarDatePicker, SingleSelectField, TextArea, SubmitButton, Button, HiddenField, CheckBoxList, PasswordField

from mediacore.model import DBSession
from mediacore.model.auth import Group, User

class UniqueUsername(FancyValidator):
    def _to_python(self, value, state):
        id = request.environ['pylons.routes_dict']['id']

        query = DBSession.query(User).filter_by(user_name=value)
        if id != 'new':
            query = query.filter(User.user_id != id)

        if query.count() != 0:
            raise Invalid(
                'User name already exists',
                value, state)
        return value

class UserForm(ListForm):
    template = 'mediacore.templates.admin.box-form'
    id = 'user-form'
    css_class = 'form'
    submit_text = None
    show_children_errors = True
    _name = 'user-form' # TODO: Figure out why this is required??

    fields = [
        TextField('display_name', validator=NotEmpty, maxlength=255),
        TextField('email_address', validator=NotEmpty, maxlength=255),
        ListFieldSet('login_details', suppress_label=True, legend='Login Details:',
                     css_classes=['details_fieldset'],
                     validator = Schema(chained_validators=[FieldsMatch('password',
                                                                        'confirm_password',
                                                                        messages={'invalidNoMatch': "Passwords do not match",})]),
                     children=[
            SingleSelectField('group', label_text='Group', options=lambda: DBSession.query(Group.group_id, Group.display_name).all()),
            TextField('user_name', maxlength=16, validator=All(PlainText(), UniqueUsername(not_empty=True))),
            PasswordField('password', validators=NotEmpty, maxlength=80, autocomplete='off'),
            PasswordField('confirm_password', validators=NotEmpty, maxlength=80),
        ]),
        SubmitButton('save', default='Save', named_button=True, css_classes=['mo', 'btn-save', 'f-rgt']),
        SubmitButton('delete', default='Delete', named_button=True, css_classes=['mo', 'btn-delete']),
    ]
