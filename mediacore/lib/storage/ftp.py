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

import logging
import os

from ftplib import FTP
from urllib2 import URLError, urlopen

from formencode import Invalid
from pylons.i18n import N_

from mediacore.lib.compat import sha1
from mediacore.lib.storage import (default_file_name, StorageURI,
    FileStorageEngine, UnsuitableEngineError)

log = logging.getLogger(__name__)

FTP_SERVER = 'ftp_server'
FTP_USERNAME = 'ftp_username'
FTP_PASSWORD = 'ftp_password'
FTP_UPLOAD_DIR = 'ftp_upload_dir'
FTP_MAX_INTEGRITY_RETRIES = 'ftp_max_integrity_retries'

HTTP_DOWNLOAD_URI = 'http_download_uri'
RTMP_SERVER_URI = 'rtmp_server_uri'

from mediacore.forms.admin.storage.ftp import FTPStorageForm

class FTPUploadError(Invalid):
    pass

class FTPStorage(FileStorageEngine):

    engine_type = u'FTPStorage'
    """A uniquely identifying string for each StorageEngine implementation."""

    default_name = N_(u'FTP Storage')
    """A user-friendly display name that identifies this StorageEngine."""

    settings_form_class = FTPStorageForm

    _default_data = {
        FTP_SERVER: '',
        FTP_USERNAME: '',
        FTP_PASSWORD: '',
        FTP_UPLOAD_DIR: '',
        FTP_MAX_INTEGRITY_RETRIES: 0,
        HTTP_DOWNLOAD_URI: '',
        RTMP_SERVER_URI: '',
    }

    def store(self, media_file, file=None, url=None, meta=None):
        """Store the given file or URL and return a unique identifier for it.

        :type media_file: :class:`~mediacore.model.media.MediaFile`
        :param media_file: The associated media file object.

        :type file: :class:`cgi.FieldStorage` or None
        :param file: A freshly uploaded file object.

        :type url: unicode or None
        :param url: A remote URL string.

        :type meta: dict
        :param meta: The metadata returned by :meth:`parse`.

        :rtype: unicode or None
        :returns: The unique ID string. Return None if not generating it here.

        :raises FTPUploadError: If storing the file fails.

        """
        file_name = default_file_name(media_file)

        file_url = os.path.join(self._data[HTTP_DOWNLOAD_URI], file_name)
        upload_dir = self._data[FTP_UPLOAD_DIR]
        stor_cmd = 'STOR ' + file_name

        ftp = self._connect()
        try:
            if upload_dir:
                ftp.cwd(upload_dir)
            ftp.storbinary(stor_cmd, file)

            # Raise a FTPUploadError if the file integrity check fails
            # TODO: Delete the file if the integrity check fails
            self._verify_upload_integrity(file, file_url)
        except FTP.all_errors, e:
            log.exception(e)
            msg = _('Could not upload the file from your FTP server: %s')\
                % e.message
            raise FTPUploadError(msg, None, None)
        finally:
            ftp.quit()

    def delete(self, unique_id):
        """Delete the stored file represented by the given unique ID.

        :type unique_id: unicode
        :param unique_id: The identifying string for this file.

        :rtype: boolean
        :returns: True if successful, False if an error occurred.

        """
        upload_dir = self._data[FTP_UPLOAD_DIR]
        ftp = self._connect()
        try:
            if upload_dir:
                ftp.cwd(upload_dir)
            ftp.delete(unique_id)
            return True
        except FTP.all_errors, e:
            log.exception(e)
            return False
        finally:
            ftp.quit()

    def get_uris(self, file):
        """Return a list of URIs from which the stored file can be accessed.

        :type unique_id: unicode
        :param unique_id: The identifying string for this file.

        :rtype: list
        :returns: All :class:`StorageURI` tuples for this file.

        """
        url = os.path.join(self._data[HTTP_DOWNLOAD_URI], file.unique_id)
        # TODO: Support RTMP
        return [StorageURI(file, 'http', url, None)]

    def _connect(self):
        """Open a connection to the FTP server."""
        data = self._data
        return FTP(data[FTP_SERVER], data[FTP_USERNAME], data[FTP_PASSWORD])

    def _verify_upload_integrity(self, file, file_url):
        """Download the given file from the URL and compare the SHA1s.

        :type file: :class:`cgi.FieldStorage`
        :param file: A freshly uploaded file object, that has just been
            sent to the FTP server.

        :type file_url: str
        :param file_url: A publicly accessible URL where the uploaded file
            can be downloaded.

        :returns: `True` if the integrity check succeeds or is disabled.

        :raises FTPUploadError: If the file cannot be downloaded after
            the max number of retries, or if the the downloaded file
            doesn't match the original.

        """
        max_tries = int(self._data[FTP_MAX_INTEGRITY_RETRIES])
        if max_tries < 1:
            return True

        file.seek(0)
        orig_hash = sha1(file.read()).hexdigest()

        # Try to download the file. Increase the number of retries, or the
        # timeout duration, if the server is particularly slow.
        # eg: Akamai usually takes 3-15 seconds to make an uploaded file
        #     available over HTTP.
        for i in xrange(max_tries):
            try:
                temp_file = urlopen(file_url)
                dl_hash = sha1(temp_file.read()).hexdigest()
                temp_file.close()
            except HTTPError, http_err:
                # Don't raise the exception now, wait until all attempts fail
                time.sleep(3)
            else:
                # If the downloaded file matches, success! Otherwise, we can
                # be pretty sure that it got corrupted during FTP transfer.
                if orig_hash == dl_hash:
                    return True
                else:
                    msg = _('The file transferred to your FTP server is '\
                            'corrupted. Please try again.')
                    raise FTPUploadError(msg, None, None)

        # Raise the exception from the last download attempt
        msg = _('Could not download the file from your FTP server: %s')\
            % http_err.message
        raise FTPUploadError(msg, None, None)

FileStorageEngine.register(FTPStorage)
