# This file is a part of MediaDrop (http://www.mediadrop.net),
# Copyright 2009-2013 MediaDrop contributors
# For the exact contribution history, see the git revision log.
# The source code contained in this file is licensed under the GPLv3 or
# (at your option) any later version.
# See LICENSE.txt in the main project directory, for more information.

from formencode.validators import Int

from mediadrop.forms import ListFieldSet, TextField
from mediadrop.forms.admin.storage import StorageForm
from mediadrop.lib.i18n import N_
from mediadrop.lib.storage.ftp import (FTP_SERVER,
    FTP_USERNAME, FTP_PASSWORD,
    FTP_UPLOAD_DIR, FTP_MAX_INTEGRITY_RETRIES,
    HTTP_DOWNLOAD_URI, RTMP_SERVER_URI)
from mediadrop.plugin import events

class FTPStorageForm(StorageForm):
    event = events.Admin.Storage.FTPStorageForm

    fields = StorageForm.fields + [
        ListFieldSet('ftp',
            suppress_label=True,
            legend=N_('FTP Server Details:'),
            children=[
                TextField('server', label_text=N_('Server Hostname')),
                TextField('user', label_text=N_('Username')),
                TextField('password', label_text=N_('Password')),
                TextField('upload_dir', label_text=N_('Subdirectory on server to upload to')),
                TextField('upload_integrity_retries', label_text=N_('How many times should MediaDrop try to verify the FTP upload before declaring it a failure?'), validator=Int()),
                TextField('http_download_uri', label_text=N_('HTTP URL to access remotely stored files')),
                TextField('rtmp_server_uri', label_text=N_('RTMP Server URL to stream remotely stored files (Optional)')),
            ]
        ),
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
        data = engine._data
        ftp = value.setdefault('ftp', {})
        ftp.setdefault('server', data.get(FTP_SERVER, None))
        ftp.setdefault('user', data.get(FTP_USERNAME, None))
        ftp.setdefault('password', data.get(FTP_PASSWORD, None))
        ftp.setdefault('upload_dir', data.get(FTP_UPLOAD_DIR, None))
        ftp.setdefault('upload_integrity_retries', data.get(FTP_MAX_INTEGRITY_RETRIES, None))
        ftp.setdefault('http_download_uri', data.get(HTTP_DOWNLOAD_URI, None))
        ftp.setdefault('rtmp_server_uri', data.get(RTMP_SERVER_URI, None))
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
        ftp = kwargs['ftp']
        engine._data[FTP_SERVER] = ftp['server']
        engine._data[FTP_USERNAME] = ftp['user']
        engine._data[FTP_PASSWORD] = ftp['password']
        engine._data[FTP_UPLOAD_DIR] = ftp['upload_dir']
        engine._data[FTP_MAX_INTEGRITY_RETRIES] = ftp['upload_integrity_retries']
        engine._data[HTTP_DOWNLOAD_URI] = ftp['http_download_uri']
        engine._data[RTMP_SERVER_URI] = ftp['rtmp_server_uri']
