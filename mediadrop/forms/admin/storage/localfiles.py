# This file is a part of MediaDrop (http://www.mediadrop.net),
# Copyright 2009-2013 MediaDrop contributors
# For the exact contribution history, see the git revision log.
# The source code contained in this file is licensed under the GPLv3 or
# (at your option) any later version.
# See LICENSE.txt in the main project directory, for more information.

from mediadrop.forms import ListFieldSet, TextField
from mediadrop.forms.admin.storage import StorageForm
from mediadrop.lib.i18n import N_
from mediadrop.plugin import events

class LocalFileStorageForm(StorageForm):
    event = events.Admin.Storage.LocalFileStorageForm

    fields = StorageForm.fields + [
        ListFieldSet('specifics',
            suppress_label=True,
            legend=N_('Options specific to Local File Storage:'),
            children=[
                TextField('path',
                    label_text=N_('Path to store files under'),
                    help_text=N_('Defaults to the "data_dir" from your INI file.'),
                ),
                TextField('rtmp_server_uri',
                    label_text=N_('RTMP Server URL'),
                    help_text=N_('Files must be accessible under the same name as they are stored with locally.'),
                ),
            ],
        )
    ] + StorageForm.buttons


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
        specifics = value.setdefault('specifics', {})
        specifics.setdefault('path', engine._data.get('path', None))
        specifics.setdefault('rtmp_server_uri', engine._data.get('rtmp_server_uri', None))
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
        specifics = kwargs['specifics']
        engine._data['path'] = specifics['path'] or None
        engine._data['rtmp_server_uri'] = specifics['rtmp_server_uri'] or None
