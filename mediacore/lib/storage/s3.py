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

from mediacore.lib.filetypes import guess_container_format, guess_media_type
from mediacore.lib.storage import (get_file_size, StorageURI, StorageEngine,
    UnsuitableEngineError)

class AmazonS3Storage(StorageEngine):

    engine_type = u'AmazonS3Storage'
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
        if file is None:
            raise UnsuitableEngineError
        raise NotImplementedError

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
        raise NotImplementedError

    def delete(self, unique_id):
        """Delete the stored file represented by the given unique ID.

        :type unique_id: unicode
        :param unique_id: The identifying string for this file.
        :rtype: boolean
        :returns: True if successful, False if an error occurred.

        """
        raise NotImplementedError

    def get_uris(self, file):
        """Return a list of URIs from which the stored file can be accessed.

        :type unique_id: unicode
        :param unique_id: The identifying string for this file.
        :rtype: list
        :returns: All :class:`StorageURI` tuples for this file.

        """
        cloudfront_http = self._data.get('cloudfront_http', None)
        cloudfront_rtmp = self._data.get('cloudfront_rtmp', None)
        if cloudfront_rtmp:
            uris.append(StorageURI(file, 'rtmp', file.unique_id, cloudfront_rtmp))
        if cloudfront_http:
            uris.append(StorageURI(file, 'http', file.unique_id, cloudfront_http))
        else:
            uris = [StorageURI(file, 'http', file.unique_id, self._data['s3_url'])]
        return uris

StorageEngine.register(AmazonS3Storage)
