# This file is a part of MediaDrop (http://www.mediadrop.net),
# Copyright 2009-2013 MediaDrop contributors
# For the exact contribution history, see the git revision log.
# The source code contained in this file is licensed under the GPLv3 or
# (at your option) any later version.
# See LICENSE.txt in the main project directory, for more information.

from formencode import Invalid
from formencode.validators import FancyValidator
from tw.api import JSSource
from tw.forms import FormFieldRepeater

from mediadrop.forms import ListFieldSet, TextField
from mediadrop.forms.admin.storage import StorageForm
from mediadrop.lib.i18n import N_, _
from mediadrop.plugin import events


# Sure this could be abstracted into something more reusable.
# But at this point there's no need. Refactor later if needed.
class TranslateableRTMPServerJSSource(JSSource):
    def render(self, *args, **kwargs):
        src = JSSource.render(self, *args, **kwargs)
        return src % {'add_url': _('Add another URL')}

rtmp_server_js = TranslateableRTMPServerJSSource("""
    window.addEvent('domready', function(){
        var fields = $('rtmp').getElement('li');
        var addButton = new Element('span', {
            'class': 'add-another clickable',
            'text': '%(add_url)s'
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

class RTMPURLValidator(FancyValidator):
    def _to_python(self, value, state=None):
        if value.startswith('rtmp://'):
            return value.rstrip('/')
        raise Invalid(_('RTMP server URLs must begin with rtmp://'),
                      value, state)

class RemoteURLStorageForm(StorageForm):
    event = events.Admin.Storage.RemoteURLStorageForm

    fields = StorageForm.fields + [
        ListFieldSet('rtmp',
            legend=N_('RTMP Servers:'),
            suppress_label=True,
            children=[
                # FIXME: Display errors from the RTMPURLValidator
                FormFieldRepeater('known_servers',
                    widget=TextField(
                        css_classes=['textfield rtmp-server-uri'],
                        validator=RTMPURLValidator(),
                    ),
                    suppress_label=True,
                    repetitions=1,
                ),
            ],
        )
    ] + StorageForm.buttons

    javascript = [rtmp_server_js]

    def display(self, value, engine, **kwargs):
        """Display the form with default values from the given StorageEngine.

        If the value dict is not fully populated, populate any missing entries
        with the values from the given StorageEngine's
        :attr:`_data <mediadrop.lib.storage.StorageEngine._data>` dict.

        :param value: A (sparse) dict of values to populate the form with.
        :type value: dict
        :param engine: An instance of the storage engine implementation.
        :type engine: :class:`mediadrop.lib.storage.StorageEngine` subclass

        """
        rtmp = value.setdefault('rtmp', {})
        rtmp.setdefault('known_servers', engine._data.get('rtmp_server_uris', ()))
        return StorageForm.display(self, value, engine, **kwargs)

    def save_engine_params(self, engine, **kwargs):
        """Map validated field values to engine data.

        Since form widgets may be nested or named differently than the keys
        in the :attr:`mediadrop.lib.storage.StorageEngine._data` dict, it is
        necessary to manually map field values to the data dictionary.

        :type engine: :class:`mediadrop.lib.storage.StorageEngine` subclass
        :param engine: An instance of the storage engine implementation.
        :param \*\*kwargs: Validated and filtered form values.
        :raises formencode.Invalid: If some post-validation error is detected
            in the user input. This will trigger the same error handling
            behaviour as with the @validate decorator.

        """
        StorageForm.save_engine_params(self, engine, **kwargs)
        rtmp = kwargs.get('rtmp', {})
        rtmp_servers = rtmp.get('known_servers', ())
        engine._data['rtmp_server_uris'] = [x for x in rtmp_servers if x]
