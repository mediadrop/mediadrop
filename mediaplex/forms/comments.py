from tw.forms import ListForm, TextField, CalendarDatePicker, SingleSelectField, TextArea, SubmitButton
from formencode.validators import Int, NotEmpty, DateConverter, DateValidator
from tw.api import WidgetsList

class PostCommentForm(ListForm):
    template = 'mediaplex.templates.comments.post'
    id = 'post-comment-form'
    css_class = 'form'

    class fields(WidgetsList):
         name = TextField(validator=NotEmpty)
         body = TextArea(attrs=dict(rows=5, cols=25))
         submit = SubmitButton(css_class='submit-image')
