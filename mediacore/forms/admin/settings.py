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

from pylons import app_globals
from pylons.i18n import N_ as _
from tw.forms import CheckBox, RadioButtonList, SingleSelectField
from tw.forms.fields import Button
from tw.forms.validators import (Bool, FancyValidator, FieldStorageUploadConverter,
    Int, OneOf, Regex, StringBool)
from webhelpers.html import literal

from mediacore.forms import (FileField, ListFieldSet, ListForm,
    ResetButton, SubmitButton, TextArea, TextField, XHTMLTextArea,
    email_validator, email_list_validator)
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

# Appearance Settings #
navbar_colors = [
    ('brown', _('Brown')),
    ('blue', _('Blue')),
    ('green', _('Green')),
    ('tan', _('Tan')),
    ('white', _('White')),
    ('purple', _('Purple')),
    ('black', _('Black')),
]

hex_validation_regex = "^#\w{3,6}$"
# End Appearance Settings #

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
    template = 'admin/box-form.html'
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
        SubmitButton('save', default=_('Save'), css_classes=['btn', 'btn-save', 'blue', 'f-rgt']),
        ResetButton('cancel', default=_('Cancel'), css_classes=['btn', 'btn-cancel']),
    ]

class DisplayForm(ListForm):
    template = 'admin/box-form.html'
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
        SubmitButton('save', default=_('Save'), css_classes=['btn', 'btn-save', 'blue', 'f-rgt']),
        ResetButton('cancel', default=_('Cancel'), css_classes=['btn', 'btn-cancel']),
    ]

class PopularityForm(ListForm):
    template = 'admin/box-form.html'
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
        SubmitButton('save', default=_('Save'), css_classes=['btn', 'btn-save', 'blue', 'f-rgt']),
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
    template = 'admin/box-form.html'
    id = 'settings-form'
    css_class = 'form'
    submit_text = None
    fields = [
        boolean_radiobuttonlist('use_embed_thumbnails', label_text=_('Automatically fetch thumbnails from YouTube, Vimeo, etc.')),
        TextField('max_upload_size', label_text=_('Max. allowed upload file size in megabytes'), validator=MegaByteValidator(not_empty=True, min=0)),
        ListFieldSet('legal_wording', suppress_label=True, legend=_('Legal Wording:'), css_classes=['details_fieldset'], children=[
            XHTMLTextArea('wording_user_uploads', label_text=_('User Uploads'), attrs=dict(rows=15, cols=25)),
        ]),
        ListFieldSet('default_wording', suppress_label=True, legend=_('Default Form Values:'), css_classes=['details_fieldset'], children=[
            TextArea('wording_additional_notes', label_text=_('Additional Notes'), attrs=dict(rows=3, cols=25)),
        ]),
        SubmitButton('save', default=_('Save'), css_classes=['btn', 'btn-save', 'blue', 'f-rgt']),
        ResetButton('cancel', default=_('Cancel'), css_classes=['btn', 'btn-cancel']),
    ]

class AnalyticsForm(ListForm):
    template = 'admin/box-form.html'
    id = 'settings-form'
    css_class = 'form'
    submit_text = None
    fields = [
        ListFieldSet('google', suppress_label=True, legend=_('Google Analytics Details:'), css_classes=['details_fieldset'], children=[
            TextField('google_analytics_uacct', maxlength=255, label_text=_('Tracking Code')),
        ]),
        SubmitButton('save', default=_('Save'), css_classes=['btn', 'btn-save', 'blue', 'f-rgt']),
        ResetButton('cancel', default=_('Cancel'), css_classes=['btn', 'btn-cancel']),
    ]

class CommentsForm(ListForm):
    template = 'admin/box-form.html'
    id = 'settings-form'
    css_class = 'form'
    submit_text = None

    fields = [
        boolean_radiobuttonlist('req_comment_approval', label_text=_('Require comments to be approved by an admin')),
        ListFieldSet('akismet', suppress_label=True, legend=_('Akismet Anti-Spam Details:'), css_classes=['details_fieldset'], children=[
            TextField('akismet_key', label_text=_('Akismet Key')),
            TextField('akismet_url', label_text=_('Akismet URL')),
        ]),
        SubmitButton('save', default=_('Save'), css_classes=['btn', 'btn-save', 'blue', 'f-rgt']),
        ResetButton('cancel', default=_('Cancel'), css_classes=['btn', 'btn-cancel']),
    ]

class APIForm(ListForm):
    template = 'admin/box-form.html'
    id = 'settings-form'
    css_class = 'form'
    submit_text = None

    fields = [
        boolean_radiobuttonlist('api_secret_key_required', label_text='Require a key to access the API'),
        ListFieldSet('key', suppress_label=True, legend='API Key:', css_classes=['details_fieldset'], children=[
            TextField('api_secret_key', label_text='Access Key'),
        ]),
        ListFieldSet('prefs', suppress_label=True, legend='API Settings:', css_classes=['details_fieldset'], children=[
            TextField('api_media_max_results', label_text='Max media results'),
            TextField('api_tree_max_depth', label_text='Max tree depth'),
        ]),
        SubmitButton('save', default='Save', css_classes=['btn', 'btn-save', 'blue', 'f-rgt']),
        ResetButton('cancel', default='Cancel', css_classes=['btn', 'btn-cancel']),
    ]

class AppearanceForm(ListForm):
    template = 'admin/box-form.html'
    id = 'settings-form'
    css_class = 'form'
    submit_text = None
    fields = [
        ListFieldSet('general', suppress_label=True, legend=_('General'),
            css_classes=['details_fieldset'],
            children=[
                FileField('appearance_logo', label_text=_('Logo'),
                    validator=FieldStorageUploadConverter(not_empty=False,
                        label_text=_('Upload Logo')),
                    css_classes=[],
                    default=lambda: app_globals.settings.get('appearance_logo', \
                                                             'logo.png'),
                    template='./admin/settings/appearance_input_field.html'),
                FileField('appearance_background_image', label_text=_('Background Image'),
                    validator=FieldStorageUploadConverter(not_empty=False,
                        label_text=_('Upload Background')),
                    css_classes=[],
                    default=lambda: app_globals.settings.get('appearance_background_image', \
                                                             'bg_image.png'),
                    template='./admin/settings/appearance_input_field.html'),
                TextField('appearance_background_color', maxlength=255,
                    label_text=_('Background color'),
                    validator=Regex(hex_validation_regex, strip=True)),
                TextField('appearance_link_color', maxlength=255,
                    label_text=_('Link color'),
                    validator=Regex(hex_validation_regex, strip=True)),
                TextField('appearance_visited_link_color', maxlength=255,
                    label_text=_('Visited Link color'),
                    validator=Regex(hex_validation_regex, strip=True)),
                TextField('appearance_text_color', maxlength=255,
                    validator=Regex(hex_validation_regex, strip=True),
                    label_text=_('Text color')),
                TextField('appearance_heading_color', maxlength=255,
                    label_text=_('Heading color'),
                    validator=Regex(hex_validation_regex, strip=True)),
                SingleSelectField('appearance_navigation_bar_color',
                    label_text=_('Navbar color'),
                    options=navbar_colors),
            ]
        ),
        ListFieldSet('options', suppress_label=True, legend=_('Options'),
            css_classes=['details_fieldset'],
            children=[
                CheckBox('appearance_enable_cooliris',
                    css_classes=['checkbox-left'],
                    label_text=_('Enable Cooliris on the Explore Page'),
                    validator=Bool(if_missing='')),
                CheckBox('appearance_enable_featured_items',
                    label_text=_('Enable Featured Items on the Explore Page'),
                    css_classes=['checkbox-left'],
                    validator=Bool(if_missing='')),
                CheckBox('appearance_enable_podcast_tab',
                    label_text=_('Enable Podcast Tab'),
                    css_classes=['checkbox-left'],
                    validator=Bool(if_missing='')),
                CheckBox('appearance_enable_user_uploads',
                    label_text=_('Enable User Uploads'),
                    css_classes=['checkbox-left'],
                    validator=Bool(if_missing='')),
                CheckBox('appearance_enable_rich_text',
                    label_text=_('Enable Rich Text Editor'),
                    css_classes=['checkbox-left'],
                    validator=Bool(if_missing='')),
                CheckBox('appearance_display_logo',
                    label_text=_('Display Logo'),
                    css_classes=['checkbox-left'],
                    validator=Bool(if_missing='')),
                CheckBox('appearance_display_background_image',
                    label_text=_('Display Background Image'),
                    css_classes=['checkbox-left'],
                    validator=Bool(if_missing='')),
            ],
            template='./admin/settings/appearance_list_fieldset.html',
        ),
        ListFieldSet('advanced', suppress_label=True, legend=_('Advanced'),
            css_classes=['details_fieldset'],
            children=[
                TextArea('appearance_custom_css',
                    label_text=_('Custom CSS'),
                    attrs=dict(rows=15, cols=25)),
                TextArea('appearance_custom_header_html',
                    label_text=_('Custom Header HTML'),
                    attrs=dict(rows=15, cols=25)),
                TextArea('appearance_custom_footer_html',
                    label_text=_('Custom Footer HTML'),
                    attrs=dict(rows=15, cols=25)),
            ],
        ),
        SubmitButton('save', default=_('Save'), css_classes=['btn', 'btn-save', 'blue', 'f-rgt']),
        ResetButton('cancel', default=_('Cancel'), css_classes=['btn', 'btn-cancel']),
    ]
