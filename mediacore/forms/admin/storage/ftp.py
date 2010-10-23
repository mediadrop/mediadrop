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

from mediacore.forms import ListFieldSet, TextField
from mediacore.forms.admin.storage import StorageForm
from mediacore.lib.storage.ftp import (FTP_SERVER,
    FTP_USERNAME, FTP_PASSWORD,
    FTP_UPLOAD_DIR, FTP_MAX_INTEGRITY_RETRIES,
    HTTP_DOWNLOAD_URI, RTMP_SERVER_URI)

class FTPStorageForm(StorageForm):

    fields = StorageForm.fields + [
        ListFieldSet('ftp',
            suppress_label=True,
            legend=_('FTP Server Details:'),
            children=[
                TextField('server', label_text=_('Server Hostname')),
                TextField('user', label_text=_('Username')),
                TextField('password', label_text=_('Password')),
                TextField('upload_dir', label_text=_('Subdirectory on server to upload to')),
                TextField('upload_integrity_retries', label_text=_('How many times should MediaCore try to verify the FTP upload before declaring it a failure?'), validator=Int()),
                TextField('http_download_uri', label_text=_('HTTP URL to access remotely stored files')),
                TextField('rtmp_server_uri', label_text=_('RTMP Server URL to stream remotely stored files (Optional)')),
            ]
        ),
    ] + StorageForm.buttons

    def display(self, value, **kwargs):
        """Display the form with default values from the engine param."""
        engine = kwargs['engine']
        data = engine._data
        ftp = value.setdefault('ftp', {})
        ftp.setdefault('server', data.get(FTP_SERVER, None))
        ftp.setdefault('user', data.get(FTP_USERNAME, None))
        ftp.setdefault('password', data.get(FTP_PASSWORD, None))
        ftp.setdefault('upload_dir', data.get(FTP_UPLOAD_DIR, None))
        ftp.setdefault('upload_integrity_retries', data.get(FTP_MAX_INTEGRITY_RETRIES, None))
        ftp.setdefault('http_download_uri', data.get(HTTP_DOWNLOAD_URI, None))
        ftp.setdefault('rtmp_server_uri', data.get(RTMP_SERVER_URI, None))
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
        StorageForm.save_engine_params(self, engine, **kwargs)
        ftp = kwargs['ftp']
        engine._data[FTP_SERVER] = ftp['server']
        engine._data[FTP_USERNAME] = ftp['user']
        engine._data[FTP_PASSWORD] = ftp['password']
        engine._data[FTP_UPLOAD_DIR] = ftp['upload_dir']
        engine._data[FTP_MAX_INTEGRITY_RETRIES] = ftp['upload_integrity_retries']
        engine._data[HTTP_DOWNLOAD_URI] = ftp['http_download_uri']
        engine._data[RTMP_SERVER_URI] = ftp['rtmp_server_uri']
