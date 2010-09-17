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

from pylons import app_globals
from pylons.i18n import _
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

class DurationValidator(FancyValidator):
    """
    Duration to Seconds Converter
    """
    def _to_python(self, value, state=None):
        try:
            return helpers.duration_to_seconds(value)
        except ValueError:
            raise formencode.Invalid(_('Please use the format HH:MM:SS'),
                                     value, state)

    def _from_python(self, value, state):
        return helpers.duration_from_seconds(value)


class AddFileForm(ListForm):
    template = 'mediacore.templates.admin.media.file-add-form'
    id = 'add-file-form'
    submit_text = None
    fields = [
        FileField('file', label_text=_('Select an encoded video or audio file on your computer'), validator=FieldStorageUploadConverter(not_empty=False, label_text='Upload')),
        SubmitButton('add_url', default=_('Add URL'), named_button=True, css_class='btn btn-add-url f-rgt'),
        TextField('url', validator=URL, suppress_label=True, attrs={'title': _('YouTube, Vimeo, Google Video, Amazon S3 or any other link')}, maxlength=255),
    ]

file_type_options = [(VIDEO, _('Video')), (AUDIO, _('Audio')), (AUDIO_DESC, _('Audio Description')), (CAPTIONS, _('Captions'))]

class EditFileForm(ListForm):
    template = 'mediacore.templates.admin.media.file-edit-form'
    submit_text = None
    _name = 'fileeditform'
    params = ['file']

    class fields(WidgetsList):
        file_type = SingleSelectField(options=file_type_options, attrs={'id': None, 'autocomplete': 'off'})
        duration = TextField(validator=DurationValidator, attrs={'id': None, 'autocomplete': 'off'})
        delete = SubmitButton(default=_('Delete file'), named_button=True, css_class='file-delete', attrs={'id': None})


class MediaForm(ListForm):
    template = 'mediacore.templates.admin.box-form'
    id = 'media-form'
    css_class = 'form'
    submit_text = None
    show_children_errors = True
    _name = 'media-form' # TODO: Figure out why this is required??

    fields = [
        SingleSelectField('podcast', label_text=_('Include in the Podcast'), help_text=_('Optional'), options=lambda: [(None, None)] + DBSession.query(Podcast.id, Podcast.title).all()),
        TextField('slug', maxlength=50),
        TextField('title', validator=TextField.validator(not_empty=True), maxlength=255),
        TextField('author_name', maxlength=50),
        TextField('author_email', validator=email_validator(not_empty=True), maxlength=255),
        XHTMLTextArea('description', attrs=dict(rows=5, cols=25)),
        CategoryCheckBoxList('categories', options=lambda: DBSession.query(Category.id, Category.name).all()),
        TextArea('tags', attrs=dict(rows=3, cols=15), help_text=_(u'e.g.: puppies, great dane, adorable')),
        TextArea('notes', label_text=_('Additional Notes'), attrs=dict(rows=3, cols=25), default=lambda: app_globals.settings['wording_additional_notes']),
        SubmitButton('save', default=_('Save'), named_button=True, css_classes=['btn', 'btn-save', 'f-rgt']),
        SubmitButton('delete', default=_('Delete'), named_button=True, css_classes=['btn', 'btn-delete', 'f-lft']),
    ]


class UpdateStatusForm(Form):
    template = 'mediacore.templates.admin.media.update-status-form'
    id = 'update-status-form'
    css_class = 'form'
    submit_text = None
    params = ['media']
    media = None
    _name = 'usf'

    class fields(WidgetsList):
        publish_on = HiddenField(validator=DateTimeConverter(format='%b %d %Y @ %H:%M'))
        update_button = SubmitButton(named_button=True, validator=NotEmpty)
