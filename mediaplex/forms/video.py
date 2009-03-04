from tw.forms import ListForm, ListFieldSet, TextField, CalendarDatePicker, SingleSelectField, TextArea, SubmitButton
from formencode.validators import Int, NotEmpty, DateConverter, DateValidator
from tw.api import WidgetsList
from mediaplex.lib import helpers

class VideoForm(ListForm):
    template = 'mediaplex.templates.admin.video.form'
    id = 'video-form'
    css_class = 'form'
    submit_text = None

    fields = [
        TextField('slug', validator=NotEmpty),
        TextField('title', validator=NotEmpty),
        TextField('author_name', validator=NotEmpty),
        TextField('author_email', validator=NotEmpty),
        TextArea('description', attrs=dict(rows=5, cols=25)),
        TextArea('notes', label_text='Additional Notes', attrs=dict(rows=5, cols=25)),
        TextField('tags'),
        ListFieldSet('details', suppress_label=True, legend='Video Details:', children=[
            TextField('length'),
            TextField('url', label_text='Video URL')
        ]),
    ]

    def display(self, value=None, **kw):
        if value is not None:
            newval = {
                'slug': value.slug,
                'title': value.title,
                'author_name': 'John Doe',
                'author_email': 'john@doe.com',
                'description': value.description,
                'tags': ', '.join([tag.name for tag in value.tags]),
                'notes': """
Bible Quotes Referenced: Daniel 1:1
S&H Quotes Pages Referenced: 587, 296
Current Reviewer: Susan Rynerson
                """,
                'details': {
                    'length': helpers.duration_from_seconds(value.length),
                    'url': value.url
                }
            }
            value = newval
        return super(VideoForm, self).display(value, **kw)
