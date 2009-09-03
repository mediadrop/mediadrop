from tw.forms import TextField, CalendarDatePicker, SingleSelectField, TextArea, ResetButton
from tw.forms.validators import Int, NotEmpty, DateConverter, DateValidator
from tw.api import WidgetsList

from simpleplex.forms import ListForm, XHTMLTextArea, SubmitButton

class PostCommentForm(ListForm):
    template = 'simpleplex.templates.comments.post'
    id = 'post-comment-form'
    css_class = 'form'

    class fields(WidgetsList):
        name = TextField(validator=NotEmpty)
        body = XHTMLTextArea(validator=NotEmpty, label_text='Comment', attrs=dict(rows=5, cols=25))
        submit = SubmitButton(css_class='mo submit-image')

class EditCommentForm(ListForm):
    template = 'simpleplex.templates.admin.comments.edit'
    id = None
    css_class = 'edit-comment-form'

    fields = [
        XHTMLTextArea('body', validator=NotEmpty, label_text='Comment', attrs=dict(rows=5, cols=25)),
        SubmitButton('submit', default='Save', css_classes=['mo', 'btn-save', 'f-rgt']),
        ResetButton(default='Cancel', css_classes=['mo', 'btn-cancel'])
    ]

