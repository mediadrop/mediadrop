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

import formencode
from pylons.i18n import N_ as _
from tw.forms import RadioButtonList, SingleSelectField
from tw.forms.validators import FancyValidator, Int, OneOf, StringBool
from webhelpers.html import literal

from mediacore.forms import ListFieldSet, ListForm, ResetButton, SubmitButton, TextArea, TextField, XHTMLTextArea, email_validator, email_list_validator
from mediacore.forms.admin.categories import category_options
from mediacore.plugin import events
from mediacore.model import MultiSetting

flash_players = [
    ('flowplayer', literal('<a href="http://flowplayer.org">FlowPlayer</a> - <a href="http://flowplayer.org/download/license_gpl.htm">GPL Licence</a> (137kB)')),
    ('jwplayer', literal('<a href="http://longtailvideo.com">JWPlayer</a> - <a href="http://creativecommons.org/licenses/by-nc-sa/3.0/">CC Non-Commercial Licence</a> (86kB)')),
]
html5_players = [
    ('html5', literal('<a href="http://diveintohtml5.org/video.html">Plain &lt;video&gt; tag</a> (0kB)')),
#    ('zencoder-video-js', literal('<a href="http://videojs.com/">Zencoder Video JS</a> - <a href="http://github.com/zencoder/video-js/blob/master/LICENSE.txt">LGPL License</a> (25kB) - Video only, supports SRT subtitles')),
#    ('jwplayer-html5', literal('<a href="http://www.longtailvideo.com/support/jw-player/jw-player-for-html5/">JWPlayer for HTML5</a> - <a href="http://creativecommons.org/licenses/by-nc-sa/3.0/">CC Non-Commercial Licence</a> (126kB)')),
#    ('sublime', literal('<a href="http://jilion.com/sublime/video">Sublime</a> - not yet available')),
]
player_types = [
    ('html5', _('Always use the selected HTML5 player')),
    ('best', _('Prefer the selected HTML5 player, but use the selected Flash player or embedded player if necessary')),
    ('flash', _('Prefer the selected Flash player, but use the selected HTML5 player or embedded player if necessary')),
]

rich_text_editors = [
    ('plain', _('Plain <textarea> fields (0kB)')),
    ('tinymce', literal('Enable <a href="http://tinymce.moxiecode.com">TinyMCE</a> for &lt;textarea&gt; fields that accept XHTML input. - <a href="http://wiki.moxiecode.com/index.php/TinyMCE:License">LGPL License</a> (281kB)')),
]

def multi_settings_options(key):
    settings = MultiSetting.query\
        .filter(MultiSetting.key==key)\
        .all()
    return [(s.id, s.value) for s in settings]

def boolean_radiobuttonlist(name, **kwargs):
    return RadioButtonList(
        name,
        options=(('true', _('Yes')), ('false', _('No'))),
        validator=OneOf(['true', 'false']),
        **kwargs
    )

def real_boolean_radiobuttonlist(name, **kwargs):
    # TODO: replace uses of boolean_radiobuttonlist with this, then scrap the old one.
    return RadioButtonList(
        name,
        options=((True, _('Yes')), (False, _('No'))),
        validator=StringBool,
        **kwargs
    )

class NotificationsForm(ListForm):
    template = 'mediacore.templates.admin.box-form'
    id = 'settings-form'
    css_class = 'form'
    submit_text = None

    fields = [
        ListFieldSet('email', suppress_label=True, legend=_('Email Notifications:'), css_classes=['details_fieldset'], children=[
            TextField('email_media_uploaded', validator=email_list_validator, label_text=_('Media Uploaded'), maxlength=255),
            TextField('email_comment_posted', validator=email_list_validator, label_text=_('Comment Posted'), maxlength=255),
            TextField('email_support_requests', validator=email_list_validator, label_text=_('Support Requested'), maxlength=255),
            TextField('email_send_from', validator=email_validator, label_text=_('Send Emails From'), maxlength=255),
        ]),
        SubmitButton('save', default=_('Save'), css_classes=['btn', 'btn-save', 'f-rgt']),
        ResetButton('cancel', default=_('Cancel'), css_classes=['btn', 'btn-cancel']),
    ]

class DisplayForm(ListForm):
    template = 'mediacore.templates.admin.box-form'
    id = 'settings-form'
    css_class = 'form'
    submit_text = None

    fields = [
        RadioButtonList('rich_text_editor',
            label_text=_('Rich Text Editing'),
            options=rich_text_editors,
            validator=OneOf([x[0] for x in rich_text_editors]),
        ),
        RadioButtonList('player_type',
            label_text=_('Preferred Media Player Type for View Pages'),
            options=player_types,
            validator=OneOf([x[0] for x in player_types]),
        ),
        RadioButtonList('flash_player',
            label_text=_('Preferred Flash Player'),
            options=flash_players,
            validator=OneOf([x[0] for x in flash_players]),
        ),
        RadioButtonList('html5_player',
            label_text=_('Preferred HTML5 Player'),
            options=html5_players,
            validator=OneOf([x[0] for x in html5_players]),
        ),
        SingleSelectField('featured_category',
            label_text=_('Featured Category'),
            options=category_options,
            validator=Int(),
        ),
        SubmitButton('save', default=_('Save'), css_classes=['btn', 'btn-save', 'f-rgt']),
        ResetButton('cancel', default=_('Cancel'), css_classes=['btn', 'btn-cancel']),
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
            legend=_('Popularity Algorithm Variables:'),
            children=[
                TextField('popularity_decay_exponent', validator=Int(not_empty=True, min=1), label_text=_('Decay Exponent')),
                TextField('popularity_decay_lifetime', validator=Int(not_empty=True, min=1), label_text=_('Decay Lifetime')),
            ]
        ),
        SubmitButton('save', default=_('Save'), css_classes=['btn', 'btn-save', 'f-rgt']),
        ResetButton('cancel', default=_('Cancel'), css_classes=['btn', 'btn-cancel']),
    ]

class MegaByteValidator(Int):
    """
    Integer Validator that accepts megabytes and translates to bytes.
    """
    def _to_python(self, value, state=None):
        try:
            value = int(value) * 1024 ** 2
        except ValueError:
            pass
        return super(MegaByteValidator, self)._to_python(value, state)

    def _from_python(self, value, state):
        try:
            value = int(value) / 1024 ** 4
        except ValueError:
            pass
        return super(MegaByteValidator, self)._from_python(value, state)

class UploadForm(ListForm):
    template = 'mediacore.templates.admin.box-form'
    id = 'settings-form'
    css_class = 'form'
    submit_text = None
    fields = [
        boolean_radiobuttonlist('use_embed_thumbnails', label_text=_('Automatically fetch thumbnails from YouTube, Vimeo, etc.')),
        TextField('max_upload_size', label_text=_('Max. allowed upload file size in megabytes'), validator=MegaByteValidator(not_empty=True, min=0)),
        ListFieldSet('remote_ftp', suppress_label=True, legend=_('Remote FTP Storage Settings (Optional)'), css_classes=['details_fieldset'], children=[
            boolean_radiobuttonlist('ftp_storage', label_text=_('Enable Remote FTP Storage for Uploaded Files?')),
            TextField('ftp_server', label_text=_('FTP Server Hostname')),
            TextField('ftp_user', label_text=_('FTP Username')),
            TextField('ftp_password', label_text=_('FTP Password')),
            TextField('ftp_upload_directory', label_text=_('Subdirectory on server to upload to')),
            TextField('ftp_download_url', label_text=_('HTTP URL to access remotely stored files')),
            TextField('ftp_upload_integrity_retries', label_text=_('How many times should MediaCore try to verify the FTP upload before declaring it a failure?'), validator=Int()),
        ]),
        ListFieldSet('legal_wording', suppress_label=True, legend=_('Legal Wording:'), css_classes=['details_fieldset'], children=[
            XHTMLTextArea('wording_user_uploads', label_text=_('User Uploads'), attrs=dict(rows=15, cols=25)),
        ]),
        ListFieldSet('default_wording', suppress_label=True, legend=_('Default Form Values:'), css_classes=['details_fieldset'], children=[
            TextArea('wording_additional_notes', label_text=_('Additional Notes'), attrs=dict(rows=3, cols=25)),
        ]),
        SubmitButton('save', default=_('Save'), css_classes=['btn', 'btn-save', 'f-rgt']),
        ResetButton('cancel', default=_('Cancel'), css_classes=['btn', 'btn-cancel']),
    ]

class AnalyticsForm(ListForm):
    template = 'mediacore.templates.admin.box-form'
    id = 'settings-form'
    css_class = 'form'
    submit_text = None
    fields = [
        ListFieldSet('google', suppress_label=True, legend=_('Google Analytics Details:'), css_classes=['details_fieldset'], children=[
            TextField('google_analytics_uacct', maxlength=255, label_text=_('Tracking Code')),
        ]),
        SubmitButton('save', default=_('Save'), css_classes=['btn', 'btn-save', 'f-rgt']),
        ResetButton('cancel', default=_('Cancel'), css_classes=['btn', 'btn-cancel']),
    ]

class CommentsForm(ListForm):
    template = 'mediacore.templates.admin.box-form'
    id = 'settings-form'
    css_class = 'form'
    submit_text = None

    fields = [
        boolean_radiobuttonlist('req_comment_approval', label_text=_('Require comments to be approved by an admin')),
        ListFieldSet('akismet', suppress_label=True, legend=_('Akismet Anti-Spam Details:'), css_classes=['details_fieldset'], children=[
            TextField('akismet_key', label_text=_('Akismet Key')),
            TextField('akismet_url', label_text=_('Akismet URL')),
        ]),
        SubmitButton('save', default=_('Save'), css_classes=['btn', 'btn-save', 'f-rgt']),
        ResetButton('cancel', default=_('Cancel'), css_classes=['btn', 'btn-cancel']),
    ]
