# This file is a part of MediaCore CE, Copyright 2009-2012 MediaCore Inc.
# The source code contained in this file is licensed under the GPL.
# See LICENSE.txt in the main project directory, for more information.

from tw.forms.validators import FieldStorageUploadConverter

from mediacore.forms import FileField, Form, ListForm, SubmitButton, TextField
from mediacore.lib.i18n import N_
from mediacore.plugin import events

class SearchForm(ListForm):
    template = 'admin/search-form.html'
    id = 'nav-search'
    method = 'get'
    fields = [
        TextField('search', label_text=N_('SEARCH...')),
        SubmitButton('go', default='Go', css_classes=['clickable nav-search-btn']),
    ]
    submit_text = None

    def post_init(self, *args, **kwargs):
        events.Admin.SearchForm(self)

class ThumbForm(ListForm):
    template = 'admin/thumb-form.html'
    id = 'thumb-form'
    css_class = 'form'
    submit_text = None

    fields = [
        FileField(
            'thumb',
            validator = FieldStorageUploadConverter(
                not_empty = True,
                messages = {
                    'empty': N_('You forgot to select an image!')
                },
            )
        ),
# TODO: Put this submit button back in, and update the javascript to remove it.
#        SubmitButton('save', default='Save', css_classes=['btn', 'btn-save', 'f-rgt']),
    ]

    def post_init(self, *args, **kwargs):
        events.Admin.ThumbForm(self)
