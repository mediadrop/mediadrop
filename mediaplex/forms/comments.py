from tw.forms import TextField, CalendarDatePicker, SingleSelectField, TextArea, SubmitButton, ResetButton
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
        submit = SubmitButton(css_class='mo submit-image')

class EditCommentForm(ListForm):
    template = 'mediaplex.templates.admin.comments.edit'
    id = None
    css_class = 'edit-comment-form'

    fields = [
        TextArea('body', validator=NotEmpty, label_text='Comment', attrs=dict(rows=5, cols=25)),
        SubmitButton('submit', default='Save', css_classes=['mo', 'btn-save', 'f-rgt']),
        ResetButton(default='Cancel', css_classes=['mo', 'btn-cancel'])
    ]
