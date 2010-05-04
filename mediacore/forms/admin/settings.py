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

from genshi.core import Markup
from tw.forms import RadioButtonList, SingleSelectField
from tw.forms.validators import Int, OneOf, StringBool

from mediacore.forms import ListFieldSet, ListForm, ResetButton, SubmitButton, TextArea, TextField, XHTMLTextArea, email_validator, email_list_validator
from mediacore.forms.admin.categories import category_options

flash_players = [
    ('flowplayer', Markup('<a href="http://flowplayer.org">FlowPlayer</a> (Flash) - <a href="http://flowplayer.org/download/license_gpl.htm">Licence</a>')),
    ('jwplayer', Markup('<a href="http://longtailvideo.com">JWPlayer</a> (Flash) - <a href="http://creativecommons.org/licenses/by-nc-sa/3.0/">Licence</a>')),
]
html5_players = [
    ('sublime', Markup('<a href="http://jilion.com/sublime/video">Sublime</a> (HTML5) - not yet available')),
    ('html5', Markup('<a href="http://diveintohtml5.org/video.html">&lt;video&gt; tag</a> (HTML5) - not fully implemented in all browsers')),
]
player_types = [
    ('best', "Automatically choose the player type for each media item based on the client browser's supported features."),
    ('flash', 'Always use the selected Flash player'),
    ('html5', 'Always use the selected HTML5 player'),
]

rich_text_editors = [
    ('tinymce', 'Enable TinyMCE for <textarea> fields that accept XHTML input.'),
    ('plain', 'Plain <textarea> fields'),
]

def boolean_radiobuttonlist(name, **kwargs):
    return RadioButtonList(
        name,
        options=(('true', 'Yes'), ('false', 'No')),
        validator=OneOf(['true', 'false']),
        **kwargs
    )

class NotificationsForm(ListForm):
    template = 'mediacore.templates.admin.box-form'
    id = 'settings-form'
    css_class = 'form'
    submit_text = None

    fields = [
        ListFieldSet('email', suppress_label=True, legend='Email Notifications:', css_classes=['details_fieldset'], children=[
            TextField('email_media_uploaded', validator=email_list_validator, maxlength=255),
            TextField('email_comment_posted', validator=email_list_validator, maxlength=255),
            TextField('email_support_requests', validator=email_list_validator, maxlength=255),
            TextField('email_send_from', validator=email_validator, label_text='Send Emails From', maxlength=255),
        ]),
        SubmitButton('save', default='Save', css_classes=['btn', 'btn-save', 'f-rgt']),
        ResetButton('cancel', default='Cancel', css_classes=['btn', 'btn-cancel']),
    ]

class DisplayForm(ListForm):
    template = 'mediacore.templates.admin.box-form'
    id = 'settings-form'
    css_class = 'form'
    submit_text = None

    fields = [
        RadioButtonList('rich_text_editor',
            label_text='Rich Text Editing',
            options=rich_text_editors,
            validator=OneOf([x[0] for x in rich_text_editors]),
        ),
        RadioButtonList('player_type',
            label_text='Preferred Media Player Type for View Pages',
            options=player_types,
            validator=OneOf([x[0] for x in player_types]),
        ),
        RadioButtonList('flash_player',
            label_text='Preferred Flash Player',
            options=flash_players,
            validator=OneOf([x[0] for x in flash_players]),
        ),
        RadioButtonList('html5_player',
            label_text='Preferred HTML5 Player',
            options=html5_players,
            validator=OneOf([x[0] for x in html5_players]),
        ),
        SingleSelectField('featured_category',
            options=category_options,
            validator=Int(),
        ),
        SubmitButton('save', default='Save', css_classes=['btn', 'btn-save', 'f-rgt']),
        ResetButton('cancel', default='Cancel', css_classes=['btn', 'btn-cancel']),
    ]

class PopularityForm(ListForm):
    template = 'mediacore.templates.admin.box-form'
    id = 'settings-form'
    css_class = 'form'
    submit_text = None

    fields = [
        ListFieldSet('popularity',
            suppress_label=True,
            css_classes=['details_fieldset'],
            legend='Popularity Algorithm Variables:',
            children=[
                TextField('popularity_decay_exponent', validator=Int(not_empty=True, min=1)),
                TextField('popularity_decay_lifetime', validator=Int(not_empty=True, min=1)),
            ]
        ),
        SubmitButton('save', default='Save', css_classes=['btn', 'btn-save', 'f-rgt']),
        ResetButton('cancel', default='Cancel', css_classes=['btn', 'btn-cancel']),
    ]

class UploadForm(ListForm):
    template = 'mediacore.templates.admin.box-form'
    id = 'settings-form'
    css_class = 'form'
    submit_text = None
    fields = [
        TextField('max_upload_size', label_text='Max. allowed upload file size in bytes', validator=Int(not_empty=True, min=1000000)),
        ListFieldSet('remote_ftp', suppress_label=True, legend='Remote FTP Storage Settings (Optional)', css_classes=['details_fieldset'], children=[
            boolean_radiobuttonlist('ftp_storage', label_text='Enable Remote FTP Storage for Uploaded Files?'),
            TextField('ftp_server', label_text='FTP Server Hostname'),
            TextField('ftp_user', label_text='FTP Username'),
            TextField('ftp_password', label_text='FTP Password'),
            TextField('ftp_upload_directory', label_text='Subdirectory on server to upload to'),
            TextField('ftp_download_url', label_text='HTTP URL to access remotely stored files'),
            TextField('ftp_upload_integrity_retries', label_text='How many times should MediaCore try to verify the FTP upload before declaring it a failure?', validator=Int()),
        ]),
        ListFieldSet('legal_wording', suppress_label=True, legend='Legal Wording:', css_classes=['details_fieldset'], children=[
            XHTMLTextArea('wording_user_uploads', label_text='User Uploads', attrs=dict(rows=15, cols=25)),
        ]),
        ListFieldSet('default_wording', suppress_label=True, legend='Default Form Values:', css_classes=['details_fieldset'], children=[
            TextArea('wording_additional_notes', label_text='Additional Notes', attrs=dict(rows=3, cols=25)),
        ]),
        SubmitButton('save', default='Save', css_classes=['btn', 'btn-save', 'f-rgt']),
        ResetButton('cancel', default='Cancel', css_classes=['btn', 'btn-cancel']),
    ]

class AnalyticsForm(ListForm):
    template = 'mediacore.templates.admin.box-form'
    id = 'settings-form'
    css_class = 'form'
    submit_text = None
    fields = [
        ListFieldSet('google', suppress_label=True, legend='Google Analytics Details:', css_classes=['details_fieldset'], children=[
            TextField('google_analytics_uacct', maxlength=255, label_text='Tracking Code'),
        ]),
        SubmitButton('save', default='Save', css_classes=['btn', 'btn-save', 'f-rgt']),
        ResetButton('cancel', default='Cancel', css_classes=['btn', 'btn-cancel']),
    ]

class CommentsForm(ListForm):
    template = 'mediacore.templates.admin.box-form'
    id = 'settings-form'
    css_class = 'form'
    submit_text = None

    fields = [
        boolean_radiobuttonlist('req_comment_approval', label_text='Require comments to be approved by an admin'),
        ListFieldSet('akismet', suppress_label=True, legend='Akismet Anti-Spam Details:', css_classes=['details_fieldset'], children=[
            TextField('akismet_key', label_text='Akismet Key'),
            TextField('akismet_url', label_text='Akismet URL'),
        ]),
        SubmitButton('save', default='Save', css_classes=['btn', 'btn-save', 'f-rgt']),
        ResetButton('cancel', default='Cancel', css_classes=['btn', 'btn-cancel']),
    ]

