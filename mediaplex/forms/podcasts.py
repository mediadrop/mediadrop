from tw.forms import ListFieldSet, TextField, FileField, CalendarDatePicker, SingleSelectField, TextArea, SubmitButton, RadioButtonList
from tw.forms.validators import Schema, Int, NotEmpty, DateConverter, DateValidator, Email
from mediaplex.lib import helpers
from mediaplex.forms import ListForm

class PodcastForm(ListForm):
    template = 'mediaplex.templates.admin.podcasts.form'
    id = 'podcast-form'
    css_class = 'form'
    submit_text = None
    params = ['podcast']
    podcast = None

    # required to support multiple named buttons to differentiate between Save & Delete?
    _name = 'vf'

    explicit_options = ['Not specified', 'Explicit', 'Clean']

    fields = [
        TextField('slug', validator=NotEmpty),
        TextField('title', validator=NotEmpty),
        TextField('subtitle'),
        TextField('author_name', validator=NotEmpty),
        TextField('author_email', validator=NotEmpty),
        TextArea('description', attrs=dict(rows=5, cols=25)),
        ListFieldSet('details', suppress_label=True, legend='Podcast Details:', children=[
            TextField('copyright'),
            TextField('category'),
            RadioButtonList('explicit', options=explicit_options),
        ]),
        SubmitButton('save', default='Save', named_button=True, css_classes=['mo', 'btn-save', 'f-rgt']),
        SubmitButton('delete', default='Delete', named_button=True, css_classes=['mo', 'btn-delete']),
    ]

