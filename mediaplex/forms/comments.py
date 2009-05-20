from tw.forms import TextField, CalendarDatePicker, SingleSelectField, TextArea, SubmitButton
from tw.forms.validators import Int, NotEmpty, DateConverter, DateValidator
from tw.api import WidgetsList

from mediaplex.forms import ListForm

class PostCommentForm(ListForm):
    template = 'mediaplex.templates.comments.post'
    id = 'post-comment-form'
    css_class = 'form'

    class fields(WidgetsList):
         name = TextField(validator=NotEmpty)
         body = TextArea(validator=NotEmpty, label_text='Comment', attrs=dict(rows=5, cols=25))
         submit = SubmitButton(css_class='submit-image')
