from tw.forms import TextField, CalendarDatePicker, SingleSelectField, TextArea, ResetButton
from tw.forms.validators import Int, NotEmpty, DateConverter, DateValidator
from tw.api import WidgetsList

from mediacore.forms import ListForm, XHTMLTextArea, SubmitButton


class PostCommentForm(ListForm):
    template = 'mediacore.templates.comments.post'
    id = 'post-comment-form'
    css_class = 'form'

    class fields(WidgetsList):
        name = TextField(validator=NotEmpty)
        body = XHTMLTextArea(validator=NotEmpty, label_text='Comment', attrs=dict(rows=5, cols=25))
        submit = SubmitButton(css_class='btn btn-post-comment')


class EditCommentForm(ListForm):
    template = 'mediacore.templates.admin.comments.edit'
    id = None
    css_class = 'edit-comment-form'

    class fields(WidgetsList):
        body = XHTMLTextArea(validator=NotEmpty, label_text='Comment', attrs=dict(rows=5, cols=25))
        submit = SubmitButton(default='Save', css_classes=['mo', 'btn-save', 'f-rgt'])
        cancel = ResetButton(default='Cancel', css_classes=['mo', 'btn-cancel'])
