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

from tw.forms import TextField, FileField
from tw.forms.validators import FieldStorageUploadConverter

from mediacore.forms import Form, ListForm, SubmitButton


class SearchForm(ListForm):
    method = 'get'
    fields = [TextField('search', label_text='SEARCH...')]
    submit_text = None


class AlbumArtForm(ListForm):
    template = 'mediacore.templates.admin.album-art-form'
    id = 'album-art-form'
    css_class = 'form'
    submit_text = None

    fields = [
        FileField(
            'album_art',
            validator = FieldStorageUploadConverter(
                not_empty = True,
                messages = {
                    'empty': 'You forgot to select an image!'
                },
            )
        ),
#        SubmitButton('save', default='Save', css_classes=['mo', 'btn-save', 'f-rgt']),
    ]
