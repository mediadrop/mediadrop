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

from pylons.i18n import _
from tw.api import WidgetsList
from tw.forms import CheckBoxList, HiddenField, SingleSelectField
from tw.forms.validators import NotEmpty

from mediacore.model.categories import Category
from mediacore.lib import helpers
from mediacore.forms import Form, ListForm, SubmitButton, TextField

def option_tree(cats):
    indent = helpers.decode_entities(u'&nbsp;') * 4
    return [(None, None)] + \
        [(c.id, indent * depth + c.name) for c, depth in cats.traverse()]

def category_options():
    return option_tree(Category.query.order_by(Category.name.asc()).populated_tree())

class CategoryForm(ListForm):
    template = 'mediacore.templates.admin.categories.form'
    id = None
    css_classes = ['category-form', 'form']
    submit_text = None

    # required to support multiple named buttons to differentiate between Save & Delete?
    _name = 'vf'

    class fields(WidgetsList):
        save = SubmitButton(default=_('Save'), named_button=True, css_classes=['f-rgt', 'btn', 'btn-save'])
        name = TextField(validator=TextField.validator(not_empty=True))
        slug = TextField(validator=NotEmpty)
        parent_id = SingleSelectField(label_text=_('Parent Category'), options=category_options)

class CategoryCheckBoxList(CheckBoxList):
    params = ['category_tree']
    template = 'mediacore.templates.admin.categories.selection_list'

class CategoryRowForm(Form):
    template = 'mediacore.templates.admin.categories.row-form'
    id = None
    submit_text = None
    params = ['category', 'depth', 'first_child']

    class fields(WidgetsList):
        name = HiddenField()
        slug = HiddenField()
        parent_id = HiddenField()
        delete = SubmitButton(default=_('Delete'), css_classes=['btn', 'btn-inline-delete'])
