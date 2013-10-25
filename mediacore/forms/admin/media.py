# This file is a part of MediaDrop (http://www.mediadrop.net),
# Copyright 2009-2013 MediaDrop contributors
# For the exact contribution history, see the git revision log.
# The source code contained in this file is licensed under the GPLv3 or
# (at your option) any later version.
# See LICENSE.txt in the main project directory, for more information.


from pylons import request
from tw.api import WidgetsList
from formencode import Invalid
from formencode.validators import FancyValidator
from tw.forms import HiddenField, SingleSelectField
from tw.forms.validators import Int, DateTimeConverter, FieldStorageUploadConverter, OneOf

from mediacore.lib import helpers
from mediacore.lib.filetypes import registered_media_types
from mediacore.lib.i18n import N_, _
from mediacore.forms import FileField, Form, ListForm, SubmitButton, TextArea, TextField, XHTMLTextArea, email_validator
from mediacore.forms.admin.categories import CategoryCheckBoxList
from mediacore.model import Category, DBSession, Podcast
from mediacore.plugin import events
from mediacore.validation import URIValidator

class DurationValidator(FancyValidator):
    """
    Duration to Seconds Converter
    """
    def _to_python(self, value, state=None):
        try:
            return helpers.duration_to_seconds(value)
        except ValueError:
            msg = _('Bad duration formatting, use Hour:Min:Sec')
            # Colons have special meaning in error messages
            msg.replace(':', '&#058;')
            raise Invalid(msg, value, state)

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
            raise Invalid(
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
            raise Invalid(u'; '.join(errors), value, state)

        if (width, height) == (0, 0):
            return (None, None)

        return width, height


    def _from_python(self, value, state):
        if value == (None, None):
            return "0x0"

        width, height = value
        return u"%dx%d" % (width, height)

class OneOfGenerator(OneOf):
    __unpackargs__ = ('generator',)
    def validate_python(self, value, state):
        if not value in self.generator():
            if self.hideList:
                raise Invalid(self.message('invalid', state), value, state)
            else:
                items = '; '.join(map(str, self.list))
                raise Invalid(
                    self.message('notIn', state, items=items, value=value),
                    value,
                    state
                )

class AddFileForm(ListForm):
    template = 'admin/media/file-add-form.html'
    id = 'add-file-form'
    submit_text = None
    
    event = events.Admin.AddFileForm
    
    fields = [
        FileField('file', label_text=N_('Select an encoded video or audio file on your computer'), validator=FieldStorageUploadConverter(not_empty=False, label_text=N_('Upload'))),
        SubmitButton('add_url', default=N_('Add URL'), named_button=True, css_class='btn grey btn-add-url f-rgt'),
        TextField('url', validator=URIValidator, suppress_label=True, attrs=lambda: {'title': _('YouTube, Vimeo, Amazon S3 or any other link')}, maxlength=255),
    ]

file_type_options = lambda: registered_media_types()
file_types = lambda: (id for id, name in registered_media_types())
file_type_validator = OneOfGenerator(file_types, if_missing=None)

class EditFileForm(ListForm):
    template = 'admin/media/file-edit-form.html'
    submit_text = None
    _name = 'fileeditform'
    params = ['file']
    
    event = events.Admin.EditFileForm
    
    class fields(WidgetsList):
        file_id = TextField(validator=Int())
        file_type = SingleSelectField(validator=file_type_validator, options=file_type_options, attrs={'id': None, 'autocomplete': 'off'})
        duration = TextField(validator=DurationValidator, attrs={'id': None, 'autocomplete': 'off'})
        width_height = TextField(validator=WXHValidator, attrs={'id': None, 'autocomplete': 'off'})
        bitrate = TextField(validator=Int, attrs={'id': None, 'autocomplete': 'off'})
        delete = SubmitButton(default=N_('Delete file'), named_button=True, css_class='file-delete', attrs={'id': None})


class MediaForm(ListForm):
    template = 'admin/box-form.html'
    id = 'media-form'
    css_class = 'form'
    submit_text = None
    show_children_errors = True
    _name = 'media-form' # TODO: Figure out why this is required??
    
    event = events.Admin.MediaForm
    
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
            container_attrs = lambda: ({'class': 'hidden'}, {})[bool(request.settings.get('wording_display_administrative_notes', ''))],
            default=lambda: request.settings['wording_administrative_notes']),
        SubmitButton('save', default=N_('Save'), named_button=True, css_classes=['btn', 'blue', 'f-rgt']),
        SubmitButton('delete', default=N_('Delete'), named_button=True, css_classes=['btn', 'f-lft']),
    ]


class UpdateStatusForm(Form):
    template = 'admin/media/update-status-form.html'
    id = 'update-status-form'
    css_class = 'form'
    submit_text = None
    params = ['media']
    media = None
    _name = 'usf'
    
    event = events.Admin.UpdateStatusForm

    class fields(WidgetsList):
        # TODO: handle format with babel localization
        publish_on = HiddenField(validator=DateTimeConverter(format='%b %d %Y @ %H:%M'))
        publish_until = HiddenField(validator=DateTimeConverter(format='%b %d %Y @ %H:%M'))
        status = HiddenField(validator=None)
        update_button = SubmitButton()
