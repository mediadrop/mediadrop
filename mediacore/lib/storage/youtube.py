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

import re

from operator import attrgetter
from urllib import urlencode

import gdata.youtube
import gdata.youtube.service

from mediacore.lib.compat import max
from mediacore.lib.filetypes import VIDEO
from mediacore.lib.i18n import N_
from mediacore.lib.storage import EmbedStorageEngine
from mediacore.lib.uri import StorageURI

class YoutubeStorage(EmbedStorageEngine):

    engine_type = u'YoutubeStorage'
    """A uniquely identifying unicode string for the StorageEngine."""

    default_name = N_(u'YouTube')

    url_pattern = re.compile(
        r'^(http(s?)://)?(\w+\.)?youtube.com/watch\?(.*&)?v=(?P<id>[^&#]+)'
    )
    """A compiled pattern object that uses named groupings for matches."""

    def _parse(self, url, id):
        """Return metadata for the given URL that matches :attr:`url_pattern`.

        :type url: unicode
        :param url: A remote URL string.

        :param \*\*kwargs: The named matches from the url match object.

        :rtype: dict
        :returns: Any extracted metadata.

        """
        yt_service = gdata.youtube.service.YouTubeService()
        yt_service.ssl = False
        entry = yt_service.GetYouTubeVideoEntry(video_id=id)
        thumb = max(entry.media.thumbnail, key=attrgetter('width'))

        return {
            'unique_id': id,
            'duration': int(entry.media.duration.seconds),
            'display_name': unicode(entry.media.title.text, 'utf-8'),
            'description': unicode(entry.media.description.text, 'utf-8'),
            'thumbnail_url': thumb.url,
            'type': VIDEO,
        }

    def get_uris(self, file):
        """Return a list of URIs from which the stored file can be accessed.

        :type unique_id: unicode
        :param unique_id: The identifying string for this file.

        :rtype: list
        :returns: All :class:`StorageURI` tuples for this file.

        """
        params = self._data.get('player_params', {})
        params = dict((k, int(v)) for k, v in params.iteritems())
        play_url = 'http://youtube%s.com/v/%s?%s' % (
            self._data.get('nocookie', False) and '-nocookie' or '',
            file.unique_id,
            urlencode(params, True),
        )
        web_url = 'http://youtube.com/watch?v=%s' % file.unique_id
        return [
            StorageURI(file, 'youtube', play_url, None),
            StorageURI(file, 'www', web_url, None),
        ]

EmbedStorageEngine.register(YoutubeStorage)
