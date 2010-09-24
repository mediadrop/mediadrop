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
import re

from urllib2 import Request, urlopen, URLError

# FIXME: This does not exist in py2.4
from xml.etree import ElementTree

from mediacore.lib.filetypes import VIDEO
from mediacore.lib.storage import (EmbedStorageEngine, StorageURI,
    UnsuitableEngineError)

log = logging.getLogger(__name__)

class BlipTVStorage(EmbedStorageEngine):

    engine_type = u'BlipTVStorage'
    """A uniquely identifying unicode string for the StorageEngine."""

    url_pattern = re.compile(r'^(http(s?)://)?(\w+\.)?blip.tv/file/(?P<id>\d+)')
    """A compiled pattern object that uses named groupings for matches."""

    def _parse(self, url, id):
        """Return metadata for the given URL that matches :attr:`url_pattern`.

        :type url: unicode
        :param url: A remote URL string.

        :param \*\*kwargs: The named matches from the url match object.

        :rtype: dict
        :returns: Any extracted metadata.

        """
        req = Request('http://blip.tv/file/%s?skin=api' % id)

        try:
            temp_data = urlopen(req)
            try:
                xmltree = ElementTree.parse(temp_data)
            finally:
                temp_data.close()
        except URLError, e:
            log.exception(e)
            raise

        root = xmltree.getroot()
        asset = root.find('payload/asset')
        log.debug('xml %r', root)
        meta = {'type': VIDEO}
        embed_lookup = asset.findtext('embedLookup')
        meta['unique_id'] = '%s %s' % (id, embed_lookup)
        meta['display_name'] = asset.findtext('title')
        meta['duration'] = int(asset.findtext('mediaList/media/duration') or 0) or None
#        meta['bitrate'] = int(root.findtext('audiobitrate') or 0)\
#                        + int(root.findtext('videobitrate') or 0) or None
        return meta

    def get_uris(self, file):
        """Return a list of URIs from which the stored file can be accessed.

        :type unique_id: unicode
        :param unique_id: The identifying string for this file.

        :rtype: list
        :returns: All :class:`StorageURI` tuples for this file.

        """
        web_id, embed_lookup = file.unique_id.split(' ')
        play_url = 'http://blip.tv/play/%s' % embed_lookup
        web_url = 'http://blip.tv/file/%s' % web_id
        return [
            StorageURI(file, 'bliptv', play_url, None),
            StorageURI(file, 'www', web_url, None),
        ]

EmbedStorageEngine.register(BlipTVStorage)
