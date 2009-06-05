from tw.forms import ListFieldSet, TextField, FileField, CalendarDatePicker, SingleSelectField, TextArea, SubmitButton
from tw.api import WidgetsList, CSSLink
from tw.forms.validators import Schema, Int, NotEmpty, DateConverter, DateValidator, Email, FieldStorageUploadConverter

from mediaplex.forms import ListForm

class VideoForm(ListForm):
    template = 'mediaplex.templates.admin.video.form'
    id = 'video-form'
    css_class = 'form'
    submit_text = None
    params = ['video']
    video = None

    # required to support multiple named buttons to differentiate between Save & Delete?
    _name = 'vf'

    fields = [
        TextField('slug', validator=NotEmpty),
        TextField('title', validator=NotEmpty),
        TextField('author_name', validator=NotEmpty),
        TextField('author_email', validator=NotEmpty),
        TextArea('description', attrs=dict(rows=5, cols=25)),
        TextArea('notes', label_text='Additional Notes', attrs=dict(rows=5, cols=25)),
        TextField('tags'),
        ListFieldSet('details', suppress_label=True, legend='Video Details:', children=[
            TextField('duration'),
            TextField('url', label_text='Video URL')
        ]),
        SubmitButton('save', default='Save', named_button=True, css_classes=['mo', 'btn-save', 'f-rgt']),
        SubmitButton('delete', default='Delete', named_button=True, css_classes=['mo', 'btn-delete']),
    ]


class AlbumArtForm(ListForm):
    template = 'mediaplex.templates.admin.video.album-art-form'
    id = 'album-art-form'
    css_class = 'form'
    submit_text = None

    fields = [
        FileField('album_art', validator=NotEmpty),
        SubmitButton('save', default='Save', css_classes=['mo', 'btn-save', 'f-rgt']),
#        ResetButton('cancel', default='Cancel', css_classes=['btn-save', 'f-rgt']),
#        SubmitButton('delete', default='Delete', css_classes=['btn-delete']),
    ]

class UploadForm(ListForm):
    template = 'mediaplex.templates.video.upload-form'
    id = 'upload-form'
    css_class = 'form'
    css = [CSSLink(link='/styles/forms.css')]
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
        file = FileField(validator=FieldStorageUploadConverter(not_empty=True, messages={'empty':'Oops! You forgot to enter a file.'}), label_text='Video File', show_error=True)
        submit = SubmitButton(css_class='submit-image', show_error=False)



