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

from urlparse import urlsplit

from pylons.i18n import N_

from mediacore.forms.admin.storage.remoteurls import RemoteURLStorageForm
from mediacore.lib.filetypes import guess_container_format, guess_media_type
from mediacore.lib.storage import (FileStorageEngine, EmbedStorageEngine,
    StorageURI, StorageEngine, UnsuitableEngineError)

log = logging.getLogger(__name__)

RTMP_SERVER_URIS = 'rtmp_server_uris'
RTMP_URI_DIVIDER = '$^'

class RemoteURLStorage(StorageEngine):

    engine_type = u'RemoteURLStorage'
    """A uniquely identifying unicode string for the StorageEngine."""

    default_name = N_(u'Remote URLs')

    second_to = [FileStorageEngine, EmbedStorageEngine]

    settings_form_class = RemoteURLStorageForm

    is_singleton = True

    _default_data = {
        RTMP_SERVER_URIS: [],
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

        if url.startswith('rtmp://'):
            known_server_uris = self._data.setdefault(RTMP_SERVER_URIS, ())

            if RTMP_URI_DIVIDER in url:
                # Allow the user to explicitly mark the server/file separation
                parts = url.split(RTMP_URI_DIVIDER)
                server_uri = parts[0].rstrip('/')
                file_uri = ''.join(parts[1:]).lstrip('/')
                if server_uri not in known_server_uris:
                    known_server_uris.append(server_uri)
            else:
                # Get the rtmp server from our list of known servers or fail
                for server_uri in known_server_uris:
                    if url.startswith(server_uri):
                        file_uri = url[len(server_uri.rstrip('/') + '/'):]
                        break
                else:
                    raise UnsuitableEngineError
            unique_id = ''.join((server_uri, RTMP_URI_DIVIDER, file_uri))
        else:
            unique_id = url

        filename = os.path.basename(url)
        name, ext = os.path.splitext(filename)
        ext = ext.lstrip('.').lower()

        container = guess_container_format(ext)

        # FIXME: Replace guess_container_format with something that takes
        #        into consideration the supported formats of all the custom
        #        players that may be installed.
#        if not container or container == 'unknown':
#            raise UnsuitableEngineError

        return {
            'type': guess_media_type(ext),
            'container': container,
            'display_name': u'%s.%s' % (name, container or ext),
            'unique_id': unique_id,
        }

    def get_uris(self, file):
        """Return a list of URIs from which the stored file can be accessed.

        :type unique_id: unicode
        :param unique_id: The identifying string for this file.
        :rtype: list
        :returns: All :class:`StorageURI` tuples for this file.

        """
        uid = file.unique_id
        if uid.startswith('rtmp://'):
            sep_index = uid.find(RTMP_URI_DIVIDER) # can raise ValueError
            if sep_index < 0:
                log.warn('File %r has an invalidly formatted unique ID for RTMP.', file)
                return []
            server_uri = uid[:sep_index]
            file_uri = uid[sep_index + len(RTMP_URI_DIVIDER)]
            return [StorageURI(file, 'rtmp', file_uri, server_uri)]
        return [StorageURI(file, 'http', file.unique_id, None)]

StorageEngine.register(RemoteURLStorage)
