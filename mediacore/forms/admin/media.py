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

from tw.api import WidgetsList
import formencode
from tw.forms import HiddenField, RadioButtonList, SingleSelectField
from tw.forms.validators import Int, StringBool, NotEmpty, DateTimeConverter, FieldStorageUploadConverter, OneOf

from mediacore.lib import helpers
from mediacore.forms import FileField, Form, ListFieldSet, ListForm, SubmitButton, TextArea, TextField, XHTMLTextArea, email_validator
from mediacore.forms.admin.categories import CategoryCheckBoxList
from mediacore.forms.admin.settings import players
from mediacore.model import Category, DBSession, MediaFile, Podcast
from mediacore.model.settings import fetch_setting

player_opts = [(None, 'Use global player defined in the settings panel.')] + players

class AddFileForm(ListForm):
    template = 'mediacore.templates.admin.media.file-add-form'
    id = 'media-file-form'
    submit_text = None
    fields = [
        FileField('file', suppress_label=True, validator=FieldStorageUploadConverter(not_empty=False, label_text='Upload', show_error=True)),
        TextField('url', label_text='URL', default='URL', suppress_label=True, maxlength=255),
    ]


class EditFileForm(ListForm):
    template = 'mediacore.templates.admin.media.file-edit-form'
    submit_text = None
    _name = 'fileeditform'
    params = ['file']

    class fields(WidgetsList):
        file_id = HiddenField(validator=Int)
        is_playable = HiddenField(validator=StringBool)
        is_embeddable = HiddenField(validator=StringBool)
        player_enabled = HiddenField(validator=StringBool)
        feed_enabled = HiddenField(validator=StringBool)
        toggle_player = SubmitButton(default='Play in the Flash Player', named_button=True, css_classes=['file-play'])
        toggle_feed = SubmitButton(default='Include in RSS feeds', named_button=True, css_classes=['file-feed'])
        delete = SubmitButton(default='Delete file', named_button=True, css_class='file-delete')

    def display(self, value=None, file=None, **kwargs):
        """Autopopulate the values when passed a file kwarg.
        Since 'file' is passed as a kwarg and is a defined param of the form,
        its accessible in the template.
        """
        if value is None and isinstance(file, MediaFile):
            value = dict(
                file_id = file.id,
                is_playable = file.is_playable and 1 or 0,
                is_embeddable = file.is_embeddable and 1 or 0,
                player_enabled = file.enable_player and 1 or 0,
                feed_enabled = file.enable_feed and 1 or 0,
            )
        return super(EditFileForm, self).display(value, file=file, **kwargs)


class DurationValidator(formencode.FancyValidator):
    """
    Duration to Seconds Converter
    """
    def _to_python(self, value, state):
        try:
            return helpers.duration_to_seconds(value)
        except ValueError:
            raise formencode.Invalid('Please use the format HH:MM:SS',
                                     value, state)

    def _from_python(self, value, state):
        return helpers.duration_from_seconds(value)


class MediaForm(ListForm):
    template = 'mediacore.templates.admin.box-form'
    id = 'media-form'
    css_class = 'form'
    submit_text = None
    show_children_errors = True
    _name = 'media-form' # TODO: Figure out why this is required??

    fields = [
        SingleSelectField('podcast', label_text='Include in the Podcast', help_text='Optional', options=lambda: [(None, None)] + DBSession.query(Podcast.id, Podcast.title).all()),
        TextField('slug', validator=NotEmpty, maxlength=50),
        TextField('title', validator=NotEmpty, maxlength=255),
        TextField('author_name', maxlength=50),
        TextField('author_email', validator=email_validator(not_empty=True), maxlength=50),
        XHTMLTextArea('description', attrs=dict(rows=5, cols=25)),
        TextArea('notes', label_text='Additional Notes', attrs=dict(rows=3, cols=25), default=lambda: fetch_setting('wording_additional_notes')),
        CategoryCheckBoxList('categories', options=lambda: DBSession.query(Category.id, Category.name).all()),
        TextArea('tags', attrs=dict(rows=3, cols=15), help_text=u'e.g.: puppies, great dane, adorable'),
        RadioButtonList('player',
            legend='Media Player for View pages:',
            options=player_opts,
            validator=OneOf([x[0] for x in player_opts]),
        ),
        ListFieldSet('details', suppress_label=True, legend='Media Details:', css_classes=['details_fieldset'], children=[
            TextField('duration', validator=DurationValidator),
        ]),
        SubmitButton('save', default='Save', named_button=True, css_classes=['btn', 'btn-save', 'f-rgt']),
        SubmitButton('delete', default='Delete', named_button=True, css_classes=['btn', 'btn-delete']),
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


class PodcastFilterForm(ListForm):
    id = 'podcastfilterform'
    method = 'get'
    template = 'mediacore.templates.admin.media.podcast-filter-form'

    fields = [SingleSelectField('podcast_filter', suppress_label=True, options=lambda: [('All Media', 'All Media')] + DBSession.query(Podcast.id, Podcast.title).all() + [('Unfiled', 'Unfiled')])]
