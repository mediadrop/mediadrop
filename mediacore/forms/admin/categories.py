# This file is a part of MediaCore CE, Copyright 2009-2012 MediaCore Inc.
# The source code contained in this file is licensed under the GPL.
# See LICENSE.txt in the main project directory, for more information.

from tw.api import WidgetsList
from tw.forms import CheckBoxList, HiddenField, SingleSelectField
from tw.forms.validators import NotEmpty

from mediacore.model.categories import Category
from mediacore.forms import Form, ListForm, ResetButton, SubmitButton, TextField
from mediacore.lib import helpers
from mediacore.lib.i18n import N_
from mediacore.plugin import events

def option_tree(cats):
    indent = helpers.decode_entities(u'&nbsp;') * 4
    return [(None, None)] + \
        [(c.id, indent * depth + c.name) for c, depth in cats.traverse()]

def category_options():
    return option_tree(Category.query.order_by(Category.name.asc()).populated_tree())

class CategoryForm(ListForm):
    template = 'admin/categories/form.html'
    id = None
    css_classes = ['category-form', 'form']
    submit_text = None

    # required to support multiple named buttons to differentiate between Save & Delete?
    _name = 'vf'

    class fields(WidgetsList):
        name = TextField(validator=TextField.validator(not_empty=True), label_text=N_('Name'))
        slug = TextField(validator=NotEmpty, label_text=N_('Permalink'))
        parent_id = SingleSelectField(label_text=N_('Parent Category'), options=category_options)
        cancel = ResetButton(default=N_('Cancel'), css_classes=['btn', 'f-lft', 'btn-cancel'])
        save = SubmitButton(default=N_('Save'), named_button=True, css_classes=['f-rgt', 'btn', 'blue', 'btn-save'])

    def post_init(self, *args, **kwargs):
        events.Admin.CategoryForm(self)

class CategoryCheckBoxList(CheckBoxList):
    params = ['category_tree']
    template = 'admin/categories/selection_list.html'

class CategoryRowForm(Form):
    template = 'admin/categories/row-form.html'
    id = None
    submit_text = None
    params = ['category', 'depth', 'first_child']

    class fields(WidgetsList):
        name = HiddenField()
        slug = HiddenField()
        parent_id = HiddenField()
        delete = SubmitButton(default=N_('Delete'), css_classes=['btn', 'table-row', 'delete', 'btn-inline-delete'])

    def post_init(self, *args, **kwargs):
        events.Admin.CategoryRowForm(self)
