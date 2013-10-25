# This file is a part of MediaDrop (http://www.mediadrop.net),
# Copyright 2009-2013 MediaDrop contributors
# For the exact contribution history, see the git revision log.
# The source code contained in this file is licensed under the GPLv3 or
# (at your option) any later version.
# See LICENSE.txt in the main project directory, for more information.

import logging
import os

from mediacore.forms.admin.storage.remoteurls import RemoteURLStorageForm
from mediacore.lib.filetypes import guess_container_format, guess_media_type
from mediacore.lib.i18n import N_, _
from mediacore.lib.storage.api import (EmbedStorageEngine, StorageEngine,
    UnsuitableEngineError, UserStorageError)
from mediacore.lib.uri import StorageURI

log = logging.getLogger(__name__)

RTMP_SERVER_URIS = 'rtmp_server_uris'
RTMP_URI_DIVIDER = '$^'

class RemoteURLStorage(StorageEngine):

    engine_type = u'RemoteURLStorage'
    """A uniquely identifying unicode string for the StorageEngine."""

    default_name = N_(u'Remote URLs')

    settings_form_class = RemoteURLStorageForm

    try_after = [EmbedStorageEngine]

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
                    raise UserStorageError(
                        _('This RTMP server has not been configured. Add it '
                          'by going to Settings > Storage Engines > '
                          'Remote URLs.'))
            unique_id = ''.join((server_uri, RTMP_URI_DIVIDER, file_uri))
        else:
            unique_id = url

        filename = os.path.basename(url)
        name, ext = os.path.splitext(filename)
        ext = unicode(ext).lstrip('.').lower()

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

    def get_uris(self, media_file):
        """Return a list of URIs from which the stored file can be accessed.

        :type media_file: :class:`~mediacore.model.media.MediaFile`
        :param media_file: The associated media file object.
        :rtype: list
        :returns: All :class:`StorageURI` tuples for this file.

        """
        uid = media_file.unique_id
        if uid.startswith('rtmp://'):
            sep_index = uid.find(RTMP_URI_DIVIDER) # can raise ValueError
            if sep_index < 0:
                log.warn('File %r has an invalidly formatted unique ID for RTMP.', media_file)
                return []
            server_uri = uid[:sep_index]
            file_uri = uid[sep_index + len(RTMP_URI_DIVIDER):]
            return [StorageURI(media_file, 'rtmp', file_uri, server_uri)]
        return [StorageURI(media_file, 'http', uid, None)]

StorageEngine.register(RemoteURLStorage)
