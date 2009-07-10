from tw.forms import ListFieldSet, TextField, FileField, CalendarDatePicker, SingleSelectField, TextArea, SubmitButton, Button
from tw.api import WidgetsList, CSSLink
from tw.forms.validators import Schema, Int, NotEmpty, DateConverter, DateValidator, Email, FieldStorageUploadConverter

from mediaplex.model import DBSession, Podcast
from mediaplex.lib import helpers
from mediaplex.forms import ListForm
from mediaplex.model import DBSession, Podcast


class MediaFileForm(ListForm):
    template = 'mediaplex.templates.admin.media.file-form'
    id = 'media-file-form'
    submit_text = None
    fields = [
        FileField('file', suppress_label=True, validator=FieldStorageUploadConverter(not_empty=False, label_text='Upload', show_error=True)),
        TextField('url', label_text='URL', default='URL', suppress_label=True),
    ]


class MediaForm(ListForm):
    template = 'mediaplex.templates.admin.box-form'
    id = 'media-form'
    css_class = 'form'
    submit_text = None
    params = ['media']
    media = None

    # required to support multiple named buttons to differentiate between Save & Delete?
    _name = 'vf'

    fields = [
        SingleSelectField('podcast', label_text='Include in the Podcast', help_text='Optional', options=lambda: [(None, None)] + DBSession.query(Podcast.id, Podcast.title).all()),
        TextField('slug', validator=NotEmpty),
        TextField('title', validator=NotEmpty),
        TextField('author_name', validator=NotEmpty),
        TextField('author_email', validator=NotEmpty),
        TextArea('description', attrs=dict(rows=5, cols=25)),
        TextArea('notes', label_text='Additional Notes', attrs=dict(rows=3, cols=25), default="""Bible References: None
S&H References: None
Reviewer: None
License: General Upload"""),
        TextField('tags'),
        ListFieldSet('details', suppress_label=True, legend='Media Details:', children=[
            TextField('duration'),
        ]),
        SubmitButton('save', default='Save', named_button=True, css_classes=['mo', 'btn-save', 'f-rgt']),
        SubmitButton('delete', default='Delete', named_button=True, css_classes=['mo', 'btn-delete']),
    ]


class UploadForm(ListForm):
    template = 'mediaplex.templates.video.upload-form'
    id = 'upload-form'
    css_class = 'form'
    css = [CSSLink(link=helpers.url_for('/styles/forms.css'))]
    show_children_errors = False
    params = ['async_action']

    class fields(WidgetsList):
        name = TextField(label_text='First Name:', help_text='(leave blank for anonymous)', show_error=True)
        email = TextField(validator=Email(not_empty=True, messages={
            'badUsername': 'The portion of the email address before the @ is invalid',
            'badDomain': 'The portion of this email address after the @ is invalid'
        }), label_text='Your email:', help_text='(will not be published)', show_error=True)
        title = TextField(validator=NotEmpty(messages={'empty':'You\'ve gotta have a title!'}), label_text='Title:', show_error=True)
        description = TextArea(validator=NotEmpty(messages={'empty':'At least give it a short description...'}), label_text='Description:', attrs=dict(rows=5, cols=25), show_error=True)
        tags = TextField(label_text='Tags:', help_text='(optional) e.g.: puppies, great dane, adorable', show_error=True)
        file = FileField(validator=FieldStorageUploadConverter(not_empty=True, messages={'empty':'Oops! You forgot to enter a file.'}), label_text='Media File', show_error=True)
        submit = SubmitButton(css_class='submit-image', show_error=False)


class PodcastFilterForm(ListForm):
    id = 'podcastfilterform'
    method = 'get'
    template = 'mediaplex.templates.admin.media.podcast-filter-form'

    fields = [SingleSelectField('podcast_filter', suppress_label=True, options=lambda: [('All Media', 'All Media')] + DBSession.query(Podcast.id, Podcast.title).all() + [('Unfiled', 'Unfiled')])]
