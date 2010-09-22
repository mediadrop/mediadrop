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

from urlparse import urlsplit

from mediacore.lib.filetypes import guess_container_format, guess_media_type
from mediacore.lib.storage import (StorageURI,
    StorageEngine, UnsuitableEngineError)

RTMP_SERVER_URI = 'rtmp_server_uri'

class RemoteURLStorage(StorageEngine):

    engine_type = u'RemoteURLStorage'
    """A uniquely identifying unicode string for the StorageEngine."""

    def parse(self, file=None, url=None):
        """Return metadata for the given file or raise an error.

        :type file: :class:`cgi.FieldStorage` or None
        :param file: A freshly uploaded file object.
        :type url: unicode or None
        :param url: A remote URL string.
        :rtype: dict
        :returns: Any extracted metadata.
        :raises UnsuitableEngineError: If file information cannot be parsed.

        """
        if url is None:
            raise UnsuitableEngineError

        filename = os.path.basename(url)
        name, ext = os.path.splitext(filename)
        ext = ext.lstrip('.').lower()

        # FIXME: Replace guess_container_format with something that takes
        #        into consideration the supported formats of all the custom
        #        players that may be installed.
        container = guess_container_format(ext)

        if not container or container == 'unknown':
            raise UnsuitableEngineError

        return {
            'type': guess_media_type(ext),
            'container': container,
            'display_name': u'%s.%s' % (name, container or ext),
            'unique_id': url,
        }

    def get_uris(self, file):
        """Return a list of URIs from which the stored file can be accessed.

        :type unique_id: unicode
        :param unique_id: The identifying string for this file.
        :rtype: list
        :returns: All :class:`StorageURI` tuples for this file.

        """
        return [StorageURI(file, 'http', file.unique_id, None)]

StorageEngine.register(RemoteURLStorage)

class RTMPRemoteURLStorage(RemoteURLStorage):

    engine_type = u'RTMPRemoteURLStorage'
    """A uniquely identifying unicode string for the StorageEngine."""

    _default_data = {
        RTMP_SERVER_URI: None,
    }

    def parse(self, file=None, url=None):
        """Return metadata for the given file or raise an error.

        :type file: :class:`cgi.FieldStorage` or None
        :param file: A freshly uploaded file object.
        :type url: unicode or None
        :param url: A remote URL string.
        :rtype: dict
        :returns: Any extracted metadata.
        :raises UnsuitableEngineError: If file information cannot be parsed.

        """
        if url is None:
            raise UnsuitableEngineError

        rtmp_server = self._data[RTMP_SERVER_URI]

        if not url.startswith(rtmp_server):
            raise UnsuitableEngineError

        # Strip off the rtmp server from the URL.
        # We only use the relative file path as the unique ID.
        url = url[len(rtmp_server.rstrip('/') + '/'):]

        return super(RTMPRemoteURLStorage, self).parse(url=url)

    def get_uris(self, file):
        """Return a list of URIs from which the stored file can be accessed.

        :type unique_id: unicode
        :param unique_id: The identifying string for this file.
        :rtype: list
        :returns: All :class:`StorageURI` tuples for this file.

        """
        rtmp_server = self._data[RTMP_SERVER_URI]
        return [StorageURI(file, 'rtmp', file.unique_id, rtmp_server)]

StorageEngine.register(RTMPRemoteURLStorage)
