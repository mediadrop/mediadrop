# This file is a part of MediaDrop (http://www.mediadrop.net),
# Copyright 2009-2013 MediaDrop contributors
# For the exact contribution history, see the git revision log.
# The source code contained in this file is licensed under the GPLv3 or
# (at your option) any later version.
# See LICENSE.txt in the main project directory, for more information.

import logging
import re

from urllib2 import urlopen, URLError

from mediadrop.lib.filetypes import VIDEO
from mediadrop.lib.i18n import N_
from mediadrop.lib.storage.api import EmbedStorageEngine
from mediadrop.lib.uri import StorageURI
from mediadrop.lib.xhtml import decode_entities

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

    def _parse(self, url, **kwargs):
        """Return metadata for the given URL that matches :attr:`url_pattern`.

        :type url: unicode
        :param url: A remote URL string.

        :param \*\*kwargs: The named matches from the url match object.

        :rtype: dict
        :returns: Any extracted metadata.

        """
        id = kwargs['id']
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

    def get_uris(self, media_file):
        """Return a list of URIs from which the stored file can be accessed.

        :type media_file: :class:`~mediadrop.model.media.MediaFile`
        :param media_file: The associated media file object.
        :rtype: list
        :returns: All :class:`StorageURI` tuples for this file.

        """
        uid = media_file.unique_id
        play_url = ('http://video.google.com/googleplayer.swf'
                    '?docid=%s'
                    '&hl=en'
                    '&fs=true') % uid
        web_url = 'http://video.google.com/videoplay?docid=%s' % uid
        return [
            StorageURI(media_file, 'googlevideo', play_url, None),
            StorageURI(media_file, 'www', web_url, None),
        ]

EmbedStorageEngine.register(GoogleVideoStorage)
