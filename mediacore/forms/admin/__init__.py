# This file is a part of MediaDrop (http://www.mediadrop.net),
# Copyright 2009-2013 MediaDrop contributors
# For the exact contribution history, see the git revision log.
# The source code contained in this file is licensed under the GPLv3 or
# (at your option) any later version.
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
    
    event = events.Admin.SearchForm

class ThumbForm(ListForm):
    template = 'admin/thumb-form.html'
    id = 'thumb-form'
    css_class = 'form'
    submit_text = None
    
    event = events.Admin.ThumbForm
    
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
