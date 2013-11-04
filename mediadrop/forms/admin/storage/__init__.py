# This file is a part of MediaDrop (http://www.mediadrop.net),
# Copyright 2009-2013 MediaDrop contributors
# For the exact contribution history, see the git revision log.
# The source code contained in this file is licensed under the GPLv3 or
# (at your option) any later version.
# See LICENSE.txt in the main project directory, for more information.

from mediadrop.forms import ListFieldSet, ListForm, SubmitButton, TextField
from mediadrop.lib.i18n import N_

class StorageForm(ListForm):
    template = 'admin/box-form.html'
    id = 'storage-form'
    css_class = 'form storageform'
    submit_text = None
    show_children_errors = True
    _name = 'storage-form' # TODO: Figure out why this is required??
    params = ['engine']

    fields = [
        ListFieldSet('general',
            legend=N_('General Options:'),
            suppress_label=True,
            children=[
                TextField('display_name',
                    label_text=N_('Display Name'),
                    validator=TextField.validator(not_empty=True),
                    maxlength=100,
                ),
            ],
        ),
    ]

    buttons = [
        SubmitButton('save',
            default=N_('Save'),
            css_classes=['btn', 'btn-save', 'blue', 'f-rgt'],
        ),
    ]

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
        general = value.setdefault('general', {})
        if not general.get('display_name', None):
            general['display_name'] = engine.display_name
        return ListForm.display(self, value, engine=engine, **kwargs)

    def save_engine_params(self, engine, general, **kwargs):
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
        engine.display_name = general['display_name']
