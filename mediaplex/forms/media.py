from tw.api import WidgetsList, CSSLink
from tw.forms.validators import Schema, Int, StringBool, NotEmpty, DateConverter, DateValidator, Email, FieldStorageUploadConverter

from mediaplex.model import DBSession, Podcast, MediaFile
from mediaplex.lib import helpers
from mediaplex.forms import Form, ListForm, ListFieldSet, TextField, XHTMLTextArea, FileField, CalendarDatePicker, SingleSelectField, TextArea, SubmitButton, Button, HiddenField, CheckBoxList
from mediaplex.model import DBSession, Podcast, Topic


class AddFileForm(ListForm):
    template = 'mediaplex.templates.admin.media.file-add-form'
    id = 'media-file-form'
    submit_text = None
    fields = [
        FileField('file', suppress_label=True, validator=FieldStorageUploadConverter(not_empty=False, label_text='Upload', show_error=True)),
        TextField('url', label_text='URL', default='URL', suppress_label=True, maxlength=255),
    ]

class EditFileForm(ListForm):
    template = 'mediaplex.templates.admin.media.file-edit-form'
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


class MediaForm(ListForm):
    template = 'mediaplex.templates.admin.box-form'
    id = 'media-form'
    css_class = 'form'
    submit_text = None
    show_children_errors = True

    fields = [
        SingleSelectField('podcast', label_text='Include in the Podcast', help_text='Optional', options=lambda: [(None, None)] + DBSession.query(Podcast.id, Podcast.title).all()),
        TextField('slug', validator=NotEmpty, maxlength=50),
        TextField('title', validator=NotEmpty, maxlength=255),
        TextField('author_name', validator=NotEmpty, maxlength=50),
        TextField('author_email', validator=NotEmpty, maxlength=50),
        XHTMLTextArea('description', attrs=dict(rows=5, cols=25)),
        TextArea('notes', label_text='Additional Notes', attrs=dict(rows=3, cols=25), default="""Bible References: None
S&H References: None
Reviewer: None
License: General Upload"""),
        CheckBoxList('topics', template='mediaplex.templates.admin.categories.selection_list', options=lambda: DBSession.query(Topic.id, Topic.name).all()),
        TextField('tags'),
        ListFieldSet('details', suppress_label=True, legend='Media Details:', css_classes=['details_fieldset'], children=[
            TextField('duration'),
        ]),
        SubmitButton('save', default='Save', named_button=True, css_classes=['mo', 'btn-save', 'f-rgt']),
        SubmitButton('delete', default='Delete', named_button=True, css_classes=['mo', 'btn-delete']),
    ]

class UpdateStatusForm(Form):
    template = 'mediaplex.templates.admin.media.update-status-form'
    id = 'update-status-form'
    css_class = 'form'
    submit_text = None
    params = ['media']
    media = None
    _name = 'usf'

    fields = [
        SubmitButton('update_button', named_button=True, validator=NotEmpty),
    ]


class UploadForm(ListForm):
    template = 'mediaplex.templates.video.upload-form'
    id = 'upload-form'
    css_class = 'form'
    css = [CSSLink(link=helpers.url_for('/styles/forms.css'))]
    show_children_errors = False
    params = ['async_action']

    class fields(WidgetsList):
        name = TextField(label_text='First Name:', help_text='(leave blank for anonymous)', show_error=True, maxlength=50)
        email = TextField(validator=Email(not_empty=True, messages={
            'badUsername': 'The portion of the email address before the @ is invalid',
            'badDomain': 'The portion of this email address after the @ is invalid'
        }), label_text='Your email:', help_text='(will not be published)', show_error=True, maxlength=50)
        title = TextField(validator=NotEmpty(messages={'empty':'You\'ve gotta have a title!'}), label_text='Title:', show_error=True, maxlength=255)
        description = XHTMLTextArea(validator=NotEmpty(messages={'empty':'At least give it a short description...'}), label_text='Description:', attrs=dict(rows=5, cols=25), show_error=True)
        tags = TextField(label_text='Tags:', help_text='(optional) e.g.: puppies, great dane, adorable', show_error=True)
        tags.validator.if_missing = ""
        file = FileField(validator=FieldStorageUploadConverter(not_empty=True, messages={'empty':'Oops! You forgot to enter a file.'}), label_text='Media File', show_error=True)
        submit = SubmitButton(css_class='submit-image', show_error=False)


class PodcastFilterForm(ListForm):
    id = 'podcastfilterform'
    method = 'get'
    template = 'mediaplex.templates.admin.media.podcast-filter-form'

    fields = [SingleSelectField('podcast_filter', suppress_label=True, options=lambda: [('All Media', 'All Media')] + DBSession.query(Podcast.id, Podcast.title).all() + [('Unfiled', 'Unfiled')])]
