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

__all__ = ['EmbedURLValidator', 'UploadForm']

import os.path

from tw.api import WidgetsList, CSSLink
from tw.forms.validators import NotEmpty, FieldStorageUploadConverter
from pylons import config
from pylons.i18n import N_

from mediacore.lib import helpers
from mediacore.forms import ListForm, TextField, XHTMLTextArea, FileField, SubmitButton, email_validator
from mediacore.plugin import events

validators = dict(
    description = XHTMLTextArea.validator(
        messages = {'empty': N_('At least give it a short description...')},
        not_empty = True,
    ),
    name = TextField.validator(
        messages = {'empty': N_("You've gotta have a name!")},
        not_empty = True,
    ),
    title = TextField.validator(
        messages = {'empty': N_("You've gotta have a title!")},
        not_empty = True,
    ),
    url = TextField.validator(
        if_missing = None,
    ),
)

class UploadForm(ListForm):
    template = 'upload/form.html'
    id = 'upload-form'
    css_class = 'form'
    show_children_errors = False
    params = ['async_action']

    class fields(WidgetsList):
        name = TextField(validator=validators['name'], label_text=N_('Your Name:'), maxlength=50)
        email = TextField(validator=email_validator(not_empty=True), label_text=N_('Your Email:'), help_text=N_('(will never be published)'), maxlength=255)
        title = TextField(validator=validators['title'], label_text=N_('Title:'), maxlength=255)
        description = XHTMLTextArea(validator=validators['description'], label_text=N_('Description:'), attrs=dict(rows=5, cols=25))
        url = TextField(validator=validators['url'], label_text=N_('Add a YouTube, Vimeo or Google Video URL:'), maxlength=255)
        file = FileField(validator=FieldStorageUploadConverter(if_missing=None, messages={'empty':N_('Oops! You forgot to enter a file.')}), label_text=N_('OR:'))
        submit = SubmitButton(default=N_('Submit'), css_classes=['mcore-btn', 'btn-submit'])

    def post_init(self, *args, **kwargs):
        events.UploadForm(self)
