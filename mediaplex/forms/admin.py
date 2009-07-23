from tw.forms import TextField, FileField, SubmitButton
from tw.forms.validators import FieldStorageUploadConverter

from mediaplex.forms import Form, ListForm


class SearchForm(ListForm):
    method = 'get'
    fields = [TextField('search', label_text='SEARCH...')]
    submit_text = None


class AlbumArtForm(ListForm):
    template = 'mediaplex.templates.admin.album-art-form'
    id = 'album-art-form'
    css_class = 'form'
    submit_text = None

    fields = [
        FileField(
            'album_art',
            validator = FieldStorageUploadConverter(
                not_empty = True,
                messages = {
                    'empty': 'You forgot to select an image!'
                },
            )
        ),
#        SubmitButton('save', default='Save', css_classes=['mo', 'btn-save', 'f-rgt']),
    ]
