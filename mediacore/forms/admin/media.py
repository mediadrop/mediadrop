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
from tw.api import WidgetsList
from formencode.validators import FancyValidator, URL
from tw.forms import HiddenField, RadioButtonList, SingleSelectField
from tw.forms.core import DefaultValidator
from tw.forms.validators import Int, StringBool, NotEmpty, DateTimeConverter, FieldStorageUploadConverter, OneOf

from mediacore.lib import helpers
from mediacore.lib.filetypes import AUDIO, AUDIO_DESC, CAPTIONS, VIDEO
from mediacore.forms import FileField, Form, ListFieldSet, ListForm, SubmitButton, TextArea, TextField, XHTMLTextArea, email_validator
from mediacore.forms.admin.categories import CategoryCheckBoxList
from mediacore.model import Category, DBSession, MediaFile, Podcast
from mediacore.plugin import events

class DurationValidator(FancyValidator):
    """
    Duration to Seconds Converter
    """
    def _to_python(self, value, state=None):
        try:
            return helpers.duration_to_seconds(value)
        except ValueError:
            raise formencode.Invalid(
                # XXX: THIS CREATES A BUG: Colons in formencode.Invalid messages are not allowed.
                _('Bad duration formatting, use Hour:Min:Sec'), value, state)

    def _from_python(self, value, state):
        return helpers.duration_from_seconds(value)

class WXHValidator(FancyValidator):
    """
    width by height validator.
    example input 1: "800x600"
    example output 2: (800, 600)

    example input 2: ""
    example output 2: (None, None)

    example input 3: "0x0"
    example output 3:" (None, None)
    """
    def _to_python(self, value, state=None):
        if not value.strip():
            return (None, None)

        try:
            width, height = value.split('x')
        except ValueError, e:
            raise formencode.Invalid(
                _('Value must be in the format wxh; e.g. 200x300'),
                value, state)
        errors = []
        try:
            width = int(width)
        except ValueError, e:
            errors.append(_('Width must be a valid integer'))
        try:
            height = int(height)
        except ValueError, e:
            errors.append(_('Height must be a valid integer'))
        if errors:
            raise formencode.Invalid(u'; '.join(errors), value, state)

        if (width, height) == (0, 0):
            return (None, None)

        return width, height


    def _from_python(self, value, state):
        if value == (None, None):
            return "0x0"

        width, height = value
        return u"%dx%d" % (width, height)

class AddFileForm(ListForm):
    template = 'mediacore.templates.admin.media.file-add-form'
    id = 'add-file-form'
    submit_text = None
    fields = [
        FileField('file', label_text=_('Select an encoded video or audio file on your computer'), validator=FieldStorageUploadConverter(not_empty=False, label_text=_('Upload'))),
        SubmitButton('add_url', default=_('Add URL'), named_button=True, css_class='btn btn-add-url f-rgt'),
        TextField('url', validator=URL, suppress_label=True, attrs={'title': _('YouTube, Vimeo, Google Video, Amazon S3 or any other link')}, maxlength=255),
    ]

    def post_init(self, *args, **kwargs):
        events.Admin.AddFileForm(self)

file_type_options = [
    (VIDEO, _('Video')),
    (AUDIO, _('Audio')),
    (AUDIO_DESC, _('Audio Description')),
    (CAPTIONS, _('Captions')),
]
file_types = [x[0] for x in file_type_options]
file_type_validator = OneOf(file_types, if_missing=None)

class EditFileForm(ListForm):
    template = 'mediacore.templates.admin.media.file-edit-form'
    submit_text = None
    _name = 'fileeditform'
    params = ['file']

    class fields(WidgetsList):
        file_id = TextField(validator=Int())
        file_type = SingleSelectField(validator=file_type_validator, options=file_type_options, attrs={'id': None, 'autocomplete': 'off'})
        duration = TextField(validator=DurationValidator(if_missing=None), attrs={'id': None, 'autocomplete': 'off'})
        width_height = TextField(validator=WXHValidator(if_missing=None), attrs={'id': None, 'autocomplete': 'off'})
        height = TextField(validator=Int(if_missing=None), attrs={'id': None, 'autocomplete': 'off'})
        max_bitrate = TextField(validator=Int(if_missing=None), attrs={'id': None, 'autocomplete': 'off'})
        delete = SubmitButton(default=_('Delete file'), named_button=True, css_class='file-delete', attrs={'id': None})

    def post_init(self, *args, **kwargs):
        events.Admin.EditFileForm(self)


class MediaForm(ListForm):
    template = 'mediacore.templates.admin.box-form'
    id = 'media-form'
    css_class = 'form'
    submit_text = None
    show_children_errors = True
    _name = 'media-form' # TODO: Figure out why this is required??

    fields = [
        SingleSelectField('podcast', label_text=_('Include in the Podcast'), help_text=_('Optional'), options=lambda: [(None, None)] + DBSession.query(Podcast.id, Podcast.title).all()),
        TextField('slug', label_text=_('Slug'), maxlength=50),
        TextField('title', label_text=_('Title'), validator=TextField.validator(not_empty=True), maxlength=255),
        TextField('author_name', label_text=_('Author Name'), maxlength=50),
        TextField('author_email', label_text=_('Author Email'), validator=email_validator(not_empty=True), maxlength=255),
        XHTMLTextArea('description', label_text=_('Description'), attrs=dict(rows=5, cols=25)),
        CategoryCheckBoxList('categories', label_text=_('Categories'), options=lambda: DBSession.query(Category.id, Category.name).all()),
        TextArea('tags', label_text=_('Tags'), attrs=dict(rows=3, cols=15), help_text=_(u'e.g.: puppies, great dane, adorable')),
        TextArea('notes', label_text=_('Additional Notes'), attrs=dict(rows=3, cols=25), default=lambda: app_globals.settings['wording_additional_notes']),
        SubmitButton('save', default=_('Save'), named_button=True, css_classes=['btn', 'btn-save', 'f-rgt']),
        SubmitButton('delete', default=_('Delete'), named_button=True, css_classes=['btn', 'btn-delete', 'f-lft']),
    ]

    def post_init(self, *args, **kwargs):
        events.Admin.MediaForm(self)


class UpdateStatusForm(Form):
    template = 'mediacore.templates.admin.media.update-status-form'
    id = 'update-status-form'
    css_class = 'form'
    submit_text = None
    params = ['media']
    media = None
    _name = 'usf'

    class fields(WidgetsList):
        # TODO: handle format with babel localization
        publish_on = HiddenField(validator=DateTimeConverter(format='%b %d %Y @ %H:%M'))
        update_button = SubmitButton(named_button=True, validator=NotEmpty)

    def post_init(self, *args, **kwargs):
        events.Admin.UpdateStatusForm(self)


class PodcastFilterForm(ListForm):
    id = 'podcastfilterform'
    method = 'get'
    template = 'mediacore.templates.admin.media.podcast-filter-form'

    fields = [SingleSelectField('podcast_filter', suppress_label=True,
        options=lambda: \
            [('All Media', _('All Media'))] + \
            DBSession.query(Podcast.id, Podcast.title).all() + \
            [('Unfiled', _('Unfiled'))])]

    def post_init(self, *args, **kwargs):
        events.Admin.PodcastFilterForm(self)
