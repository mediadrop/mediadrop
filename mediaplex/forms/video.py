from tw.forms import ListForm, ListFieldSet, TextField, FileField, CalendarDatePicker, SingleSelectField, TextArea, SubmitButton
from formencode.validators import Int, NotEmpty, DateConverter, DateValidator
from tw.api import WidgetsList

class VideoForm(ListForm):
    template = 'mediaplex.templates.admin.video.form'
    id = 'video-form'
    css_class = 'form'
    submit_text = None
    params = ['video']
    video = None

    fields = [
        # main box fields
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
        SubmitButton('save', default='Save', css_classes=['btn-save', 'f-rgt']),
        SubmitButton('delete', default='Delete', css_classes=['btn-delete']),
    ]


class AlbumArtForm(ListForm):
    template = 'mediaplex.templates.admin.video.album-art-form'
    id = 'album-art-form'
    css_class = 'form'
    submit_text = None

    fields = [
        FileField('album_art'),
        SubmitButton('save', default='Save', css_classes=['btn-save', 'f-rgt']),
#        ResetButton('cancel', default='Cancel', css_classes=['btn-save', 'f-rgt']),
#        SubmitButton('delete', default='Delete', css_classes=['btn-delete']),
    ]
