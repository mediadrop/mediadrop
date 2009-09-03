from tw.forms import TextField, CalendarDatePicker, SingleSelectField, TextArea
from tw.forms.validators import Int, NotEmpty, DateConverter, DateValidator
from tw.api import WidgetsList

from simpleplex.forms import ListForm, SubmitButton

class EditCategoryForm(ListForm):
    template = 'simpleplex.templates.admin.categories.edit'
    id = None
    css_class = 'edit-category-form'
    submit_text = None

    # required to support multiple named buttons to differentiate between Save & Delete?
    _name = 'vf'

    fields = [
        SubmitButton('submit', default='Save', named_button=True, css_classes=['f-rgt', 'mo', 'clickable', 'save-category']),
        SubmitButton('delete', default='Delete', named_button=True, css_classes=['mo', 'clickable', 'delete-category']),
        TextField('name', css_classes=['category-name'], validator=NotEmpty),
        TextField('slug', css_classes=['category-slug'], validator=NotEmpty),
    ]


