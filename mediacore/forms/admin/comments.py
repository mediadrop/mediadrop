# This file is a part of MediaDrop (http://www.mediadrop.net),
# Copyright 2009-2013 MediaDrop contributors
# For the exact contribution history, see the git revision log.
# The source code contained in this file is licensed under the GPLv3 or
# (at your option) any later version.
# See LICENSE.txt in the main project directory, for more information.

from tw.forms.validators import NotEmpty
from tw.api import WidgetsList

from mediacore.forms import ListForm, ResetButton, SubmitButton, TextArea
from mediacore.lib.i18n import N_
from mediacore.plugin import events

class EditCommentForm(ListForm):
    template = 'admin/comments/edit.html'
    id = None
    css_class = 'edit-comment-form'
    
    event = events.Admin.EditCommentForm
    
    class fields(WidgetsList):
        body = TextArea(validator=NotEmpty, label_text=N_('Comment'), attrs=dict(rows=5, cols=25))
        submit = SubmitButton(default=N_('Save'), css_classes=['btn', 'btn-save', 'blue', 'f-rgt'])
        cancel = ResetButton(default=N_('Cancel'), css_classes=['btn', 'btn-cancel'])

