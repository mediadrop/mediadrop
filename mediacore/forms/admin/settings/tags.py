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

from tw.forms import TextField, HiddenField
from tw.forms.validators import NotEmpty

from mediacore.forms import Form, ListForm, SubmitButton

class TagForm(ListForm):
    template = 'mediacore.templates.admin.settings.tags.form'
    id = None
    css_classes = ['form', 'tag-form']
    submit_text = None

    # required to support multiple named buttons to differentiate between Save & Delete?
    _name = 'vf'

    fields = [
        SubmitButton('save', default='Save', css_classes=['f-rgt', 'btn', 'btn-save']),
        TextField('name', css_classes=['tag-name'], validator=NotEmpty),
        TextField('slug', css_classes=['tag-slug'], validator=NotEmpty),
    ]

class TagRowForm(Form):
    template = 'mediacore.templates.admin.settings.tags.row-form'
    id = None
    submit_text = None
    params = ['tag']

    fields = [
        HiddenField('name'),
        HiddenField('slug'),
        SubmitButton('delete', default='Delete', css_classes=['btn', 'btn-inline-delete']),
    ]
