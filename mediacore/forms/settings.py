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

from tw.forms import TextField, CalendarDatePicker, SingleSelectField, TextArea, ResetButton, RadioButtonList
from tw.forms.validators import Schema, FieldsMatch, StringBool
from tw.api import WidgetsList

from mediacore.forms import ListForm, XHTMLTextArea, SubmitButton, ListFieldSet, PasswordField, email_validator

class SettingsForm(ListForm):
    template = 'mediacore.templates.admin.box-form'
    id = 'settings-form'
    css_class = 'form'
    submit_text = None

    fields = [
        ListFieldSet('email', suppress_label=True, legend='Email Notifications:', css_classes=['details_fieldset'], children=[
            TextField('media_uploaded', maxlength=255),
            TextField('comment_posted', maxlength=255),
            TextField('support_requests', maxlength=255),
            TextField('send_from', validator=email_validator, label_text='Send Emails From', maxlength=255),
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
        ListFieldSet('default_wording', suppress_label=True, legend='Default Form Values:', css_classes=['details_fieldset'], children=[
            TextArea('additional_notes', label_text='Additional Notes', attrs=dict(rows=3, cols=25)),
        ]),
        SubmitButton('save', default='Save', css_classes=['mo', 'btn-save', 'f-rgt']),
        ResetButton('cancel', default='Cancel', css_classes=['mo', 'btn-cancel']),
    ]

class DisplaySettingsForm(ListForm):
    template = 'mediacore.templates.admin.box-form'
    id = 'settings-form'
    css_class = 'form'
    submit_text = None

    fields = [
        RadioButtonList('tinymce',
            label_text='Rich Text Editing',
            options=[
                [True, 'Enable TinyMCE for <textarea> fields that accept XHTML input. Use of TinyMCE is not strictly XHTML compliant, but works in FF>=1.5, Safari>=3, IE>=5.5, so long as javascript is enabled.'],
                [False, 'Plain <textarea> fields']
            ],
            validator=StringBool(not_empty=True)
        ),
        SubmitButton('save', default='Save', css_classes=['mo', 'btn-save', 'f-rgt']),
        ResetButton('cancel', default='Cancel', css_classes=['mo', 'btn-cancel']),
    ]
