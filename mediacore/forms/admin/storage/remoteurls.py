# This file is a part of MediaCore, Copyright 2010 Simple Station Inc.
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

from formencode.validators import Int
from pylons.i18n import N_ as _
from tw.api import JSSource
from tw.forms import FormFieldRepeater

from mediacore.forms import ListFieldSet, TextField
from mediacore.forms.admin.storage import StorageForm

rtmp_server_js = JSSource("""
    window.addEvent('domready', function(){
        var fields = $('rtmp').getElement('li');
        var addButton = new Element('span', {
            'class': 'add-another clickable',
            'text': 'Add another URL'
        });
        addButton.inject(fields, 'bottom').addEvent('click', function(){
            var lastInput = addButton.getPrevious();
            var fullname = lastInput.get('name');
            var sepindex = fullname.indexOf('-') + 1;
            var name = fullname.substr(0, sepindex);
            var nextNum = fullname.substr(sepindex).toInt() + 1;
            var el = new Element('input', {
                'type': 'text',
                'name': name + nextNum,
                'class': 'textfield repeatedtextfield rtmp-server-uri'
            });
            el.inject(lastInput, 'after').focus();
        });
    });
""", location='headbottom')

class RemoteURLStorageForm(StorageForm):

    fields = StorageForm.fields + [
        ListFieldSet('rtmp',
            legend=_('RTMP Servers:'),
            suppress_label=True,
            children=[
                FormFieldRepeater('known_servers',
                    widget=TextField(css_classes=['textfield rtmp-server-uri']),
                    suppress_label=True,
                    repetitions=1,
                ),
            ],
        )
    ] + StorageForm.buttons

    javascript = [rtmp_server_js]

    def display(self, value, **kwargs):
        engine = kwargs['engine']
        rtmp = value.setdefault('rtmp', {})
        rtmp.setdefault('known_servers', engine._data.get('rtmp_server_uris', ()))
        return StorageForm.display(self, value, **kwargs)

    def save_engine_params(self, engine, **kwargs):
        """Map validated field values to engine data.

        Since form widgets may be nested or named differently than the keys
        in the :attr:`mediacore.lib.storage.StorageEngine._data` dict, it is
        necessary to manually map field values to the data dictionary.

        :type engine: :class:`mediacore.lib.storage.StorageEngine` subclass
        :param engine: An instance of the storage engine implementation.
        :param \*\*kwargs: Validated and filtered form values.
        :raises formencode.Invalid: If some post-validation error is detected
            in the user input. This will trigger the same error handling
            behaviour as with the @validate decorator.

        """
        rtmp = kwargs.get('rtmp', {})
        rtmp_servers = rtmp.get('known_servers', ())
        engine._data['rtmp_server_uris'] = [x for x in rtmp_servers if x]
