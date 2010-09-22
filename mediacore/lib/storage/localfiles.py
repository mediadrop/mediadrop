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

import os

from shutil import copyfileobj
from urlparse import urlunsplit

from pylons import config

from mediacore.lib.helpers import delete_files, url_for
from mediacore.lib.storage import (default_file_name, StorageURI,
    FileStorageEngine, UnsuitableEngineError)

class LocalFileStorage(FileStorageEngine):

    engine_type = u'LocalFileStorage'
    """A uniquely identifying unicode string for the StorageEngine."""

    def store(self, file=None, url=None, media_file=None, meta=None):
        """Store the given file or URL and return a unique identifier for it.

        :type file: :class:`cgi.FieldStorage` or None
        :param file: A freshly uploaded file object.
        :type url: unicode or None
        :param url: A remote URL string.
        :type media_file: :class:`~mediacore.model.media.MediaFile`
        :param media_file: The associated media file object.
        :type meta: dict
        :param meta: The metadata returned by :meth:`parse`.
        :rtype: unicode or None
        :returns: The unique ID string. Return None if not generating it here.

        """
        file_name = default_file_name(media_file)
        file_path = self._get_path(file_name)

        temp_file = file.file
        temp_file.seek(0)
        permanent_file = open(file_path, 'wb')
        copyfileobj(temp_file, permanent_file)
        temp_file.close()
        permanent_file.close()

        return file_name

    def delete(self, unique_id):
        """Delete the stored file represented by the given unique ID.

        :type unique_id: unicode
        :param unique_id: The identifying string for this file.
        :rtype: boolean
        :returns: True if successful, False if an error occurred.

        """
        file_path = self._get_path(file)
        return delete_files(file_path, 'media')

    def get_uris(self, file):
        """Return a list of URIs from which the stored file can be accessed.

        :type unique_id: unicode
        :param unique_id: The identifying string for this file.
        :rtype: list
        :returns: All :class:`StorageURI` tuples for this file.

        """
        uris = []

        # Remotely accessible URL
        url = url_for(controller='/media', action='serve', id=file.id,
                      slug=file.media.slug, container=file.container,
                      qualified=True)
        uris.append(StorageURI(file, 'http', url, None))

        # Remotely *download* accessible URL
        url = url_for(controller='/media', action='serve', id=file.id,
                      slug=file.media.slug, container=file.container,
                      qualified=True, download=1)
        uris.append(StorageURI(file, 'download', url, None))

        # Internal file URI that will be used by MediaController.serve
        path = urlunsplit(('file', '', self._get_path(file.unique_id), '', ''))
        uris.append(StorageURI(file, 'file', path, None))

        return uris

    def _get_path(self, unique_id):
        """Return the local file path for the given unique ID.

        This method is exclusive to this engine.
        """
        basepath = self._data.get('path', None)
        if not basepath:
            basepath = config['media_dir']
        return os.path.join(basepath, unique_id)

FileStorageEngine.register(LocalFileStorage)
