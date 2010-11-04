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
import simplejson

from urllib2 import Request, urlopen, URLError

from pylons.i18n import N_

from mediacore import USER_AGENT
from mediacore.lib.compat import max
from mediacore.lib.filetypes import VIDEO
from mediacore.lib.xhtml import decode_entities
from mediacore.lib.storage import (EmbedStorageEngine, StorageURI,
    UnsuitableEngineError)

log = logging.getLogger(__name__)

class GoogleVideoStorage(EmbedStorageEngine):

    engine_type = u'GoogleVideoStorage'
    """A uniquely identifying unicode string for the StorageEngine."""

    default_name = N_(u'Google Video')

    url_pattern = re.compile(
        r'^(http(s?)://)?video.google.com/videoplay\?(.*&)?docid=(?P<id>-?\d+)'
    )
    """A compiled pattern object that uses named groupings for matches."""

    xml_thumb = re.compile(r'media:thumbnail url="([^"]*)"')
    xml_duration = re.compile(r'duration="([^"]*)"')
    xhtml_title = re.compile(r'<title>([^<]*)</title>')

    def _parse(self, url, id):
        """Return metadata for the given URL that matches :attr:`url_pattern`.

        :type url: unicode
        :param url: A remote URL string.

        :param \*\*kwargs: The named matches from the url match object.

        :rtype: dict
        :returns: Any extracted metadata.

        """
        meta = {
            'unique_id': id,
            'type': VIDEO,
        }

        google_play_url = 'http://video.google.com/videoplay?docid=%s' % id
        google_data_url = 'http://video.google.com/videofeed?docid=%s' % id

        # Fetch the video title from the main video player page
        try:
            temp_data = urlopen(google_play_url)
            data = temp_data.read()
            temp_data.close()
        except URLError, e:
            log.exception(e)
        else:
            title_match = self.xhtml_title.search(data)
            if title_match:
                meta['display_name'] = title_match.group(1)

        # Fetch the meta data from a MediaRSS feed for this video
        try:
            temp_data = urlopen(google_data_url)
            data = temp_data.read()
            temp_data.close()
        except URLError, e:
            log.exception(e)
        else:
            thumb_match = self.xml_thumb.search(data)
            duration_match = self.xml_duration.search(data)
            if thumb_match:
                meta['thumbnail_url'] = decode_entities(thumb_match.group(1))
            if duration_match:
                meta['duration'] = int(duration_match.group(1))

        return meta

    def get_uris(self, file):
        """Return a list of URIs from which the stored file can be accessed.

        :type unique_id: unicode
        :param unique_id: The identifying string for this file.

        :rtype: list
        :returns: All :class:`StorageURI` tuples for this file.

        """
        play_url = ('http://video.google.com/googleplayer.swf'
                    '?docid=%s'
                    '&hl=en'
                    '&fs=true') % file.unique_id
        web_url = 'http://video.google.com/videoplay?docid=%s' % file.unique_id
        return [
            StorageURI(file, 'googlevideo', play_url, None),
            StorageURI(file, 'www', web_url, None),
        ]

EmbedStorageEngine.register(GoogleVideoStorage)
