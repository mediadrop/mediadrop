from tw.forms import TextField, CalendarDatePicker, SingleSelectField, TextArea, SubmitButton, ResetButton
from tw.forms.validators import Int, NotEmpty, DateConverter, DateValidator
from tw.api import WidgetsList

from mediaplex.forms import ListForm

class EditCategoryForm(ListForm):
    template = 'mediaplex.templates.admin.categories.edit'
    id = None
    css_class = 'edit-category-form'

    fields = [
        TextField('name', validator=NotEmpty),
        TextField('slug', validator=NotEmpty),
        SubmitButton('submit', default='Save', css_classes=['mo', 'btn-save', 'f-rgt']),
        ResetButton(default='Cancel', css_classes=['mo', 'btn-cancel'])
    ]


