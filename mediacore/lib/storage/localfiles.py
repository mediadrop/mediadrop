# This file is a part of MediaDrop (http://www.mediadrop.net),
# Copyright 2009-2013 MediaDrop contributors
# For the exact contribution history, see the git revision log.
# The source code contained in this file is licensed under the GPLv3 or
# (at your option) any later version.
# See LICENSE.txt in the main project directory, for more information.

import os

from shutil import copyfileobj
from urlparse import urlunsplit

from pylons import config

from mediacore.forms.admin.storage.localfiles import LocalFileStorageForm
from mediacore.lib.i18n import N_
from mediacore.lib.storage.api import safe_file_name, FileStorageEngine
from mediacore.lib.uri import StorageURI
from mediacore.lib.util import delete_files, url_for

class LocalFileStorage(FileStorageEngine):

    engine_type = u'LocalFileStorage'
    """A uniquely identifying unicode string for the StorageEngine."""

    default_name = N_(u'Local File Storage')

    settings_form_class = LocalFileStorageForm
    """Your :class:`mediacore.forms.Form` class for changing :attr:`_data`."""

    _default_data = {
        'path': None,
        'rtmp_server_uri': None,
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

        """
        file_name = safe_file_name(media_file, file.filename)
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
        file_path = self._get_path(unique_id)
        return delete_files([file_path], 'media')

    def get_uris(self, media_file):
        """Return a list of URIs from which the stored file can be accessed.

        :type media_file: :class:`~mediacore.model.media.MediaFile`
        :param media_file: The associated media file object.
        :rtype: list
        :returns: All :class:`StorageURI` tuples for this file.

        """
        uris = []

        # Remotely accessible URL
        url = url_for(controller='/media', action='serve', id=media_file.id,
                      slug=media_file.media.slug, container=media_file.container,
                      qualified=True)
        uris.append(StorageURI(media_file, 'http', url, None))

        # An optional streaming RTMP URI
        rtmp_server_uri = self._data.get('rtmp_server_uri', None)
        if rtmp_server_uri:
            uris.append(StorageURI(media_file, 'rtmp', media_file.unique_id, rtmp_server_uri))

        # Remotely *download* accessible URL
        url = url_for(controller='/media', action='serve', id=media_file.id,
                      slug=media_file.media.slug, container=media_file.container,
                      qualified=True, download=1)
        uris.append(StorageURI(media_file, 'download', url, None))

        # Internal file URI that will be used by MediaController.serve
        path = urlunsplit(('file', '', self._get_path(media_file.unique_id), '', ''))
        uris.append(StorageURI(media_file, 'file', path, None))

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
