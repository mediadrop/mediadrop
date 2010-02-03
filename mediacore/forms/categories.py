# This file is a part of MediaCore, Copyright 2009 Simple Station Inc.
#
# MediaCore is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# MediaCore is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from tw.forms import TextField, CalendarDatePicker, SingleSelectField, TextArea
from tw.forms.validators import Int, NotEmpty, DateConverter, DateValidator
from tw.api import WidgetsList

from mediacore.forms import ListForm, SubmitButton

class EditCategoryForm(ListForm):
    template = 'mediacore.templates.admin.categories.edit'
    id = None
    css_class = 'edit-category-form'
    submit_text = None

    # required to support multiple named buttons to differentiate between Save & Delete?
    _name = 'vf'

    fields = [
        SubmitButton('save', default='Save', named_button=True, css_classes=['f-rgt', 'mo', 'clickable', 'save-category']),
        SubmitButton('delete', default='Delete', named_button=True, css_classes=['mo', 'clickable', 'delete-category']),
        TextField('name', css_classes=['category-name'], validator=NotEmpty),
        TextField('slug', css_classes=['category-slug'], validator=NotEmpty),
    ]
