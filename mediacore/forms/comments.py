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

from tw.forms import TextField, CalendarDatePicker, SingleSelectField, TextArea, ResetButton
from tw.forms.validators import Int, NotEmpty, DateConverter, DateValidator
from tw.api import WidgetsList

from mediacore.forms import ListForm, XHTMLTextArea, SubmitButton


class PostCommentForm(ListForm):
    template = 'mediacore.templates.comments.post'
    id = 'post-comment-form'
    css_class = 'form'

    class fields(WidgetsList):
        name = TextField(validator=NotEmpty)
        body = XHTMLTextArea(validator=NotEmpty, label_text='Comment', attrs=dict(rows=5, cols=25))
        submit = SubmitButton(default='Post Comment', css_class='btn btn-post-comment')


class EditCommentForm(ListForm):
    template = 'mediacore.templates.admin.comments.edit'
    id = None
    css_class = 'edit-comment-form'

    class fields(WidgetsList):
        body = XHTMLTextArea(validator=NotEmpty, label_text='Comment', attrs=dict(rows=5, cols=25))
        submit = SubmitButton(default='Save', css_classes=['mo', 'btn-save', 'f-rgt'])
        cancel = ResetButton(default='Cancel', css_classes=['mo', 'btn-cancel'])
