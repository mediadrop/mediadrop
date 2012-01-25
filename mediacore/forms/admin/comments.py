# This file is a part of MediaCore CE, Copyright 2009-2012 MediaCore Inc.
# The source code contained in this file is licensed under the GPL.
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

    class fields(WidgetsList):
        body = TextArea(validator=NotEmpty, label_text=N_('Comment'), attrs=dict(rows=5, cols=25))
        submit = SubmitButton(default=N_('Save'), css_classes=['btn', 'btn-save', 'blue', 'f-rgt'])
        cancel = ResetButton(default=N_('Cancel'), css_classes=['btn', 'btn-cancel'])

    def post_init(self, *args, **kwargs):
        events.Admin.EditCommentForm(self)
