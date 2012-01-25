# This file is a part of MediaCore CE, Copyright 2009-2012 MediaCore Inc.
# The source code contained in this file is licensed under the GPL.
# See LICENSE.txt in the main project directory, for more information.

import re

from tw.forms import HiddenField
from tw.forms.validators import FancyValidator, NotEmpty

from mediacore.forms import Form, ListForm, SubmitButton, ResetButton, TextField
from mediacore.lib.i18n import N_
from mediacore.plugin import events

excess_whitespace = re.compile('\s\s+', re.M)

class TagNameValidator(FancyValidator):
    def _to_python(self, value, state=None):
        value = value.strip()
        value = excess_whitespace.sub(' ', value)
        if super(TagNameValidator, self)._to_python:
            value = super(TagNameValidator, self)._to_python(value, state)
        return value

class TagForm(ListForm):
    template = 'admin/tags/form.html'
    id = None
    css_classes = ['form', 'tag-form']
    submit_text = None

    # required to support multiple named buttons to differentiate between Save & Delete?
    _name = 'vf'

    fields = [
        TextField('name', label_text=N_('Name'), css_classes=['tag-name'], validator=TagNameValidator(not_empty=True)),
        TextField('slug', label_text=N_('Permalink'), css_classes=['tag-slug'], validator=NotEmpty),
        ResetButton('cancel', default=N_('Cancel'), css_classes=['btn', 'f-lft', 'btn-cancel']),
        SubmitButton('save', default=N_('Save'), css_classes=['f-rgt', 'btn', 'blue', 'btn-save']),
    ]

    def post_init(self, *args, **kwargs):
        events.Admin.TagForm(self)

class TagRowForm(Form):
    template = 'admin/tags/row-form.html'
    id = None
    submit_text = None
    params = ['tag']

    fields = [
        HiddenField('name'),
        HiddenField('slug'),
        SubmitButton('delete', default=N_('Delete'), css_classes=['btn', 'table-row', 'delete', 'btn-inline-delete']),
    ]

    def post_init(self, *args, **kwargs):
        events.Admin.TagRowForm(self)
