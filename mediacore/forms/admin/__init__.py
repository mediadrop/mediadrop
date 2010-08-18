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

from pylons.i18n import N_ as _
from tw.forms.validators import FieldStorageUploadConverter

from mediacore.forms import FileField, Form, ListForm, TextField
from mediacore.plugin import events

class SearchForm(ListForm):
    method = 'get'
    fields = [TextField('search', label_text=_('SEARCH...'))]
    submit_text = None

    def post_init(self, *args, **kwargs):
        events.Admin.SearchForm(self)

class ThumbForm(ListForm):
    template = 'mediacore.templates.admin.thumb-form'
    id = 'thumb-form'
    css_class = 'form'
    submit_text = None

    fields = [
        FileField(
            'thumb',
            validator = FieldStorageUploadConverter(
                not_empty = True,
                messages = {
                    'empty': _('You forgot to select an image!')
                },
            )
        ),
# TODO: Put this submit button back in, and update the javascript to remove it.
#        SubmitButton('save', default='Save', css_classes=['btn', 'btn-save', 'f-rgt']),
    ]

    def post_init(self, *args, **kwargs):
        events.Admin.ThumbForm(self)
