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
from pylons.i18n import N_, _
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
                _('Bad duration formatting, use Hour&#058;Min&#058;Sec'), value, state)

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
    template = 'admin/media/file-add-form.html'
    id = 'add-file-form'
    submit_text = None
    fields = [
        FileField('file', label_text=N_('Select an encoded video or audio file on your computer'), validator=FieldStorageUploadConverter(not_empty=False, label_text=N_('Upload'))),
        SubmitButton('add_url', default=N_('Add URL'), named_button=True, css_class='btn grey btn-add-url f-rgt'),
        TextField('url', validator=URL, suppress_label=True, attrs=lambda: {'title': _('YouTube, Vimeo, Google Video, Amazon S3 or any other link')}, maxlength=255),
    ]

    def post_init(self, *args, **kwargs):
        events.Admin.AddFileForm(self)

file_type_options = lambda: (
    (VIDEO, _('Video')),
    (AUDIO, _('Audio')),
    (AUDIO_DESC, _('Audio Description')),
    (CAPTIONS, _('Captions')),
)
file_types = [x[0] for x in file_type_options()]
file_type_validator = OneOf(file_types, if_missing=None)
file_type_validator = None

class EditFileForm(ListForm):
    template = 'admin/media/file-edit-form.html'
    submit_text = None
    _name = 'fileeditform'
    params = ['file']

    class fields(WidgetsList):
        file_id = TextField(validator=Int())
        file_type = SingleSelectField(validator=file_type_validator, options=file_type_options, attrs={'id': None, 'autocomplete': 'off'})
        duration = TextField(validator=DurationValidator, attrs={'id': None, 'autocomplete': 'off'})
        width_height = TextField(validator=WXHValidator, attrs={'id': None, 'autocomplete': 'off'})
        bitrate = TextField(validator=Int, attrs={'id': None, 'autocomplete': 'off'})
        delete = SubmitButton(default=N_('Delete file'), named_button=True, css_class='file-delete', attrs={'id': None})

    def post_init(self, *args, **kwargs):
        events.Admin.EditFileForm(self)


class MediaForm(ListForm):
    template = 'admin/box-form.html'
    id = 'media-form'
    css_class = 'form'
    submit_text = None
    show_children_errors = True
    _name = 'media-form' # TODO: Figure out why this is required??

    fields = [
        SingleSelectField('podcast', label_text=N_('Include in the Podcast'), css_classes=['dropdown-select'], help_text=N_('Optional'), options=lambda: [(None, None)] + DBSession.query(Podcast.id, Podcast.title).all()),
        TextField('slug', label_text=N_('Permalink'), maxlength=50),
        TextField('title', label_text=N_('Title'), validator=TextField.validator(not_empty=True), maxlength=255),
        TextField('author_name', label_text=N_('Author Name'), maxlength=50),
        TextField('author_email', label_text=N_('Author Email'), validator=email_validator(not_empty=True), maxlength=255),
        XHTMLTextArea('description', label_text=N_('Description'), attrs=dict(rows=5, cols=25)),
        CategoryCheckBoxList('categories', label_text=N_('Categories'), options=lambda: DBSession.query(Category.id, Category.name).all()),
        TextArea('tags', label_text=N_('Tags'), attrs=dict(rows=3, cols=15), help_text=N_(u'e.g.: puppies, great dane, adorable')),
        TextArea('notes',
            label_text=N_('Administrative Notes'),
            attrs=dict(rows=3, cols=25),
            container_attrs = lambda: ({'class': 'hidden'}, {})[bool(app_globals.settings.get('wording_display_administrative_notes', ''))],
            default=lambda: app_globals.settings['wording_administrative_notes']),
        SubmitButton('save', default=N_('Save'), named_button=True, css_classes=['btn', 'blue', 'f-rgt']),
        SubmitButton('delete', default=N_('Delete'), named_button=True, css_classes=['btn', 'f-lft']),
    ]

    def post_init(self, *args, **kwargs):
        events.Admin.MediaForm(self)


class UpdateStatusForm(Form):
    template = 'admin/media/update-status-form.html'
    id = 'update-status-form'
    css_class = 'form'
    submit_text = None
    params = ['media']
    media = None
    _name = 'usf'

    class fields(WidgetsList):
        # TODO: handle format with babel localization
        publish_on = HiddenField(validator=DateTimeConverter(format='%b %d %Y @ %H:%M'))
        status = HiddenField(validator=None)
        update_button = SubmitButton()

    def post_init(self, *args, **kwargs):
        events.Admin.UpdateStatusForm(self)
