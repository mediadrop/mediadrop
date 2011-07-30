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

from mediacore.lib.compat import ElementTree
from mediacore.lib.filetypes import VIDEO
from mediacore.lib.i18n import N_, _
from mediacore.lib.storage import EmbedStorageEngine, UserStorageError
from mediacore.lib.uri import StorageURI

log = logging.getLogger(__name__)

class BlipTVStorage(EmbedStorageEngine):

    engine_type = u'BlipTVStorage'
    """A uniquely identifying unicode string for the StorageEngine."""

    default_name = N_(u'BlipTV')

    url_pattern = re.compile(r'^(http(s?)://)?(\w+\.)?blip.tv/(?P<id>.+)')
    """A compiled pattern object that uses named groupings for matches."""

    def _parse(self, url, id, **kwargs):
        """Return metadata for the given URL that matches :attr:`url_pattern`.

        :type url: unicode
        :param url: A remote URL string.

        :param \*\*kwargs: The named matches from the url match object.

        :rtype: dict
        :returns: Any extracted metadata.

        """
        if '?' in url:
            url += '&skin=api'
        else:
            url += '?skin=api'

        req = Request(url)

        try:
            temp_data = urlopen(req)
            xmlstring = temp_data.read()
            try:
                try:
                    xmltree = ElementTree.fromstring(xmlstring)
                except:
                    temp_data.close()
                    raise
            except SyntaxError:
                raise UserStorageError(
                    _('Invalid BlipTV URL. This video does not exist.'))
        except URLError, e:
            log.exception(e)
            raise

        asset = xmltree.find('payload/asset')
        meta = {'type': VIDEO}
        embed_lookup = asset.findtext('embedLookup')
        meta['unique_id'] = '%s %s' % (id, embed_lookup)
        meta['display_name'] = asset.findtext('title')
        meta['description'] = asset.findtext('description')
        meta['duration'] = int(asset.findtext('mediaList/media/duration') or 0) or None
#        meta['bitrate'] = int(xmltree.findtext('audiobitrate') or 0)\
#                        + int(xmltree.findtext('videobitrate') or 0) or None
        return meta

    def get_uris(self, media_file):
        """Return a list of URIs from which the stored file can be accessed.

        :type media_file: :class:`~mediacore.model.media.MediaFile`
        :param media_file: The associated media file object.
        :rtype: list
        :returns: All :class:`StorageURI` tuples for this file.

        """
        web_id, embed_lookup = media_file.unique_id.split(' ')
        play_url = 'http://blip.tv/play/%s' % embed_lookup

        # Old blip.tv URLs had a numeric ID in the URL, now they're wordy.
        try:
            web_url = 'http://blip.tv/file/%s' % int(web_id, 10)
        except ValueError:
            web_url = 'http://blip.tv/%s' % web_id

        return [
            StorageURI(media_file, 'bliptv', play_url, None),
            StorageURI(media_file, 'www', web_url, None),
        ]

EmbedStorageEngine.register(BlipTVStorage)
