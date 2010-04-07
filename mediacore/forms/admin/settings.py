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

from tw.forms import TextField, TextArea, ResetButton, RadioButtonList
from tw.forms.validators import StringBool, Int, OneOf

from mediacore.forms import ListForm, XHTMLTextArea, SubmitButton, ListFieldSet, email_validator
from genshi.core import Markup

players = [
    ('flowplayer', Markup('FlowPlayer (Flash). <a href="http://flowplayer.org">Website</a> - <a href="http://flowplayer.org/download/license_gpl.htm">Licence</a>')),
    ('jwplayer', Markup('JWPlayer (Flash). <a href="http://longtailvideo.com">Website</a> - <a href="http://creativecommons.org/licenses/by-nc-sa/3.0/">Licence</a>')),
    ('sublime', Markup('Sublime (HTML5). <a href="http://jilion.com/sublime/video">Website</a> - not yet available')),
    ('html5', Markup('&lt;video&gt; tag (HTML5). <a href="http://diveintohtml5.org/video.html">Website</a> - not fully implemented in all browsers')),
]

class NotificationsForm(ListForm):
    template = 'mediacore.templates.admin.box-form'
    id = 'settings-form'
    css_class = 'form'
    submit_text = None

    fields = [
        ListFieldSet('email', suppress_label=True, legend='Email Notifications:', css_classes=['details_fieldset'], children=[
            TextField('email_media_uploaded', maxlength=255),
            TextField('email_comment_posted', maxlength=255),
            TextField('email_support_requests', maxlength=255),
            TextField('email_send_from', validator=email_validator, label_text='Send Emails From', maxlength=255),
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

class DisplaySettingsForm(ListForm):
    template = 'mediacore.templates.admin.box-form'
    id = 'settings-form'
    css_class = 'form'
    submit_text = None

    fields = [
        RadioButtonList('enable_tinymce',
            label_text='Rich Text Editing',
            options=[
                (True, 'Enable TinyMCE for <textarea> fields that accept XHTML input. Use of TinyMCE is not strictly XHTML compliant, but works in FF>=1.5, Safari>=3, IE>=5.5, so long as javascript is enabled.'),
                (False, 'Plain <textarea> fields')
            ],
            validator=StringBool(not_empty=True)
        ),
        ListFieldSet('popularity',
            suppress_label=True,
            css_classes=['details_fieldset'],
            legend='Popularity Algorithm Variables:',
            children=[
                TextField('popularity_decay_exponent', validator=Int(not_empty=True, min=1)),
                TextField('popularity_decay_lifetime', validator=Int(not_empty=True, min=1)),
            ]
        ),
        RadioButtonList('player',
            legend='Media Player for View pages:',
            options=players,
            validator=OneOf([x[0] for x in players]),
        ),
        SubmitButton('save', default='Save', css_classes=['btn', 'btn-save', 'f-rgt']),
        ResetButton('cancel', default='Cancel', css_classes=['btn', 'btn-cancel']),
    ]
