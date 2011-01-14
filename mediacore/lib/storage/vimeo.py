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

from mediacore import USER_AGENT
from mediacore.lib.filetypes import VIDEO
from mediacore.lib.i18n import N_
from mediacore.lib.storage import EmbedStorageEngine
from mediacore.lib.uri import StorageURI

log = logging.getLogger(__name__)

class VimeoStorage(EmbedStorageEngine):

    engine_type = u'VimeoStorage'
    """A uniquely identifying unicode string for the StorageEngine."""

    default_name = N_(u'Vimeo')

    url_pattern = re.compile(r'^(http(s?)://)?(\w+\.)?vimeo.com/(?P<id>\d+)')
    """A compiled pattern object that uses named groupings for matches."""

    def _parse(self, url, id):
        """Return metadata for the given URL that matches :attr:`url_pattern`.

        :type url: unicode
        :param url: A remote URL string.

        :param \*\*kwargs: The named matches from the url match object.

        :rtype: dict
        :returns: Any extracted metadata.

        """
        vimeo_data_url = 'http://vimeo.com/api/v2/video/%s.%s' % (id, 'json')

        # Vimeo API requires us to give a user-agent, to avoid 403 errors.
        headers = {'User-Agent': USER_AGENT}
        req = Request(vimeo_data_url, headers=headers)

        try:
            temp_data = urlopen(req)
            try:
                data = simplejson.loads(temp_data.read())[0]
            finally:
                temp_data.close()
        except URLError, e:
            log.exception(e)
            data = {}

        return {
            'unique_id': id,
            'description': unicode(data.get('description', u'')),
            'duration': int(data.get('duration', 0)),
            'display_name': unicode(data.get('title', u'')),
            'thumbnail_url': data.get('thumbnail_large', None),
            'type': VIDEO,
        }

    def get_uris(self, file):
        """Return a list of URIs from which the stored file can be accessed.

        :type unique_id: unicode
        :param unique_id: The identifying string for this file.

        :rtype: list
        :returns: All :class:`StorageURI` tuples for this file.

        """
        play_url = 'http://player.vimeo.com/video/%s' % file.unique_id
        web_url = 'http://vimeo.com/%s' % file.unique_id
        return [
            StorageURI(file, 'vimeo', play_url, None),
            StorageURI(file, 'www', web_url, None),
        ]

EmbedStorageEngine.register(VimeoStorage)
