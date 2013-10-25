# This file is a part of MediaDrop (http://www.mediadrop.net),
# Copyright 2009-2013 MediaDrop contributors
# For the exact contribution history, see the git revision log.
# The source code contained in this file is licensed under the GPLv3 or
# (at your option) any later version.
# See LICENSE.txt in the main project directory, for more information.

import logging
import re
import simplejson

from urllib import urlencode
from urllib2 import Request, urlopen, URLError

from mediacore import USER_AGENT
from mediacore.lib.filetypes import VIDEO
from mediacore.lib.i18n import N_, _
from mediacore.lib.storage.api import EmbedStorageEngine, UserStorageError
from mediacore.lib.uri import StorageURI

log = logging.getLogger(__name__)

class DailyMotionStorage(EmbedStorageEngine):

    engine_type = u'DailyMotionStorage'
    """A uniquely identifying unicode string for the StorageEngine."""

    default_name = N_(u'Daily Motion')

    url_pattern = re.compile(
        r'^(http(s?)://)?(\w+\.)?dailymotion.(\w+.?\w*)/video/(?P<id>[^_\?&#]+)_'
    )
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
        # Ensure the video uses the .com TLD for the API request.
        url = 'http://www.dailymotion.com/video/%s' % id
        data_url = 'http://www.dailymotion.com/services/oembed?' + \
            urlencode({'format': 'json', 'url': url})

        headers = {'User-Agent': USER_AGENT}
        req = Request(data_url, headers=headers)

        try:
            temp_data = urlopen(req)
            try:
                data_string = temp_data.read()
                if data_string == 'This video cannot be embeded.':
                    raise UserStorageError(
                        _('This DailyMotion video does not allow embedding.'))
                data = simplejson.loads(data_string)
            finally:
                temp_data.close()
        except URLError, e:
            log.exception(e)
            data = {}

        return {
            'unique_id': id,
            'display_name': unicode(data.get('title', u'')),
            'thumbnail_url': data.get('thumbnail_url', None),
            'type': VIDEO,
        }

    def get_uris(self, media_file):
        """Return a list of URIs from which the stored file can be accessed.

        :type media_file: :class:`~mediacore.model.media.MediaFile`
        :param media_file: The associated media file object.
        :rtype: list
        :returns: All :class:`StorageURI` tuples for this file.

        """
        uid = media_file.unique_id
        play_url = 'http://www.dailymotion.com/embed/video/%s' % uid
        web_url = 'http://www.dailymotion.com/video/%s' % uid
        return [
            StorageURI(media_file, 'dailymotion', play_url, None),
            StorageURI(media_file, 'www', web_url, None),
        ]

EmbedStorageEngine.register(DailyMotionStorage)
