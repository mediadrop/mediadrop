from tw.forms import TextField, CalendarDatePicker, SingleSelectField, TextArea, ResetButton
from tw.forms.validators import Schema, FieldsMatch
from tw.api import WidgetsList

from simpleplex.forms import ListForm, XHTMLTextArea, SubmitButton, ListFieldSet, PasswordField

class SettingsForm(ListForm):
    template = 'simpleplex.templates.admin.box-form'
    id = 'settings-form'
    css_class = 'form'
    submit_text = None

    fields = [
        ListFieldSet('email', suppress_label=True, legend='Email Notifications:', css_classes=['details_fieldset'], children=[
            TextField('media_uploaded', maxlength=255),
            TextField('comment_posted', maxlength=255),
            TextField('support_requests', maxlength=255),
            TextField('send_from', label_text='Send Emails From', maxlength=255),
        ]),
#        ListFieldSet('ftp', suppress_label=True, legend='Remote FTP File Storage:',
#                     css_classes=['details_fieldset'],
#                     help_text='If ftp_storage is enabled, then media_dir is not used for storing uploaded media files, and they are instead uploaded to the FTP server',
#                     validator = Schema(chained_validators=[FieldsMatch('password',
#                                                                        'confirm_password',
#                                                                        messages={'invalidNoMatch': "Passwords do not match",})]),
#                     children=[
#            TextField('server', maxlength=255),
#            TextField('username', maxlength=255),
#            PasswordField('password', maxlength=80, autocomplete='off'),
#            PasswordField('confirm_password', maxlength=80),
#            TextField('upload_path', maxlength=255, help_text='Absolute, or relative to login home dir'),
#            TextField('download_url', maxlength=255, label_text='Download URL'),
#        ]),
        ListFieldSet('legal_wording', suppress_label=True, legend='Legal Wording:', css_classes=['details_fieldset'], children=[
            XHTMLTextArea('user_uploads', label_text='User Uploads', attrs=dict(rows=15, cols=25)),
        ]),
        SubmitButton('save', default='Save', css_classes=['mo', 'btn-save', 'f-rgt']),
        ResetButton('cancel', default='Cancel', css_classes=['mo', 'btn-cancel']),
    ]
