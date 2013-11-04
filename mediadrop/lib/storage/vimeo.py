# This file is a part of MediaDrop (http://www.mediadrop.net),
# Copyright 2009-2013 MediaDrop contributors
# For the exact contribution history, see the git revision log.
# The source code contained in this file is licensed under the GPLv3 or
# (at your option) any later version.
# See LICENSE.txt in the main project directory, for more information.

import logging
import re
import simplejson

from urllib2 import Request, urlopen, URLError

from mediadrop import USER_AGENT
from mediadrop.lib.filetypes import VIDEO
from mediadrop.lib.i18n import N_
from mediadrop.lib.storage.api import EmbedStorageEngine
from mediadrop.lib.uri import StorageURI

log = logging.getLogger(__name__)

class VimeoStorage(EmbedStorageEngine):

    engine_type = u'VimeoStorage'
    """A uniquely identifying unicode string for the StorageEngine."""

    default_name = N_(u'Vimeo')

    url_pattern = re.compile(r'^(http(s?)://)?(\w+\.)?vimeo.com/(?P<id>\d+)')
    """A compiled pattern object that uses named groupings for matches."""

    def _parse(self, url, **kwargs):
        """Return metadata for the given URL that matches :attr:`url_pattern`.

        :type url: unicode
        :param url: A remote URL string.

        :param \*\*kwargs: The named matches from the url match object.

        :rtype: dict
        :returns: Any extracted metadata.

        """
        id = kwargs['id']
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

    def get_uris(self, media_file):
        """Return a list of URIs from which the stored file can be accessed.

        :type media_file: :class:`~mediadrop.model.media.MediaFile`
        :param media_file: The associated media file object.
        :rtype: list
        :returns: All :class:`StorageURI` tuples for this file.

        """
        uid = media_file.unique_id
        play_url = 'http://player.vimeo.com/video/%s' % uid
        web_url = 'http://vimeo.com/%s' % uid
        return [
            StorageURI(media_file, 'vimeo', play_url, None),
            StorageURI(media_file, 'www', web_url, None),
        ]

EmbedStorageEngine.register(VimeoStorage)
