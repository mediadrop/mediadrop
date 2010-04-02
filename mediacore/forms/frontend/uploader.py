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

from tw.api import WidgetsList, CSSLink
import formencode
from tw.forms.validators import NotEmpty, FieldStorageUploadConverter
from tg import config

from mediacore.lib import helpers
from mediacore.forms import ListForm, TextField, XHTMLTextArea, FileField, SubmitButton, email_validator

class EmbedURLValidator(formencode.FancyValidator):
    def _to_python(self, value, state):
        if value:
            for info in config.embeddable_filetypes.itervalues():
                match = info['pattern'].match(value)
                if match:
                    return value
            else:
                raise formencode.Invalid(("This isn't a valid YouTube, "
                                          "Google Video or Vimeo URL."),
                                         value, state)
        return value

class UploadForm(ListForm):
    template = 'mediacore.templates.media.upload-form'
    id = 'upload-form'
    css_class = 'form'
    css = [CSSLink(link=helpers.url_for('/styles/forms.css'))]
    show_children_errors = False
    params = ['async_action']

    class fields(WidgetsList):
        name = TextField(validator=NotEmpty(messages={'empty':"You've gotta have a name!"}), label_text='Your Name:', show_error=True, maxlength=50)
        email = TextField(validator=email_validator(not_empty=True), label_text='Your Email:', help_text='(will never be published)', show_error=True, maxlength=50)
        title = TextField(validator=NotEmpty(messages={'empty':"You've gotta have a title!"}), label_text='Title:', show_error=True, maxlength=255)
        description = XHTMLTextArea(validator=NotEmpty(messages={'empty':'At least give it a short description...'}), label_text='Description:', attrs=dict(rows=5, cols=25), show_error=True)
        tags = TextField(label_text='Tags:', help_text='(optional) e.g.: puppies, great dane, adorable', show_error=True)
        tags.validator.if_missing = ""
        url = TextField(validator=EmbedURLValidator(if_missing=None), label_text='Add a YouTube, Vimeo or Google Video URL:', show_error=True, maxlength=255)
        file = FileField(validator=FieldStorageUploadConverter(if_missing=None, messages={'empty':'Oops! You forgot to enter a file.'}), label_text='OR:', show_error=True)
        submit = SubmitButton(show_error=False, css_classes=['btn', 'btn-submit'])
