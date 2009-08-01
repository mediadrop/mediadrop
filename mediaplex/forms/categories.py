from tw.forms import TextField, CalendarDatePicker, SingleSelectField, TextArea, SubmitButton, ResetButton
from tw.forms.validators import Int, NotEmpty, DateConverter, DateValidator
from tw.api import WidgetsList

from mediaplex.forms import ListForm

class EditCategoryForm(ListForm):
    template = 'mediaplex.templates.admin.categories.edit'
    id = None
    css_class = 'edit-category-form'

    fields = [
        ResetButton(default='Cancel', css_classes=['mo', 'cancel-category']),
        TextField('name', css_classes=['category-name'], validator=NotEmpty),
        TextField('slug', css_classes=['category-slug'], validator=NotEmpty),
        SubmitButton('submit', default='Save', css_classes=['mo', 'clickable', 'save-category']),
    ]


