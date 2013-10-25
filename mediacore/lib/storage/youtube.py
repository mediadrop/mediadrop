# This file is a part of MediaDrop (http://www.mediadrop.net),
# Copyright 2009-2013 MediaDrop contributors
# For the exact contribution history, see the git revision log.
# The source code contained in this file is licensed under the GPLv3 or
# (at your option) any later version.
# See LICENSE.txt in the main project directory, for more information.

import re

from operator import attrgetter
from urllib import urlencode

import gdata.service
import gdata.youtube
import gdata.youtube.service

from mediacore.lib.compat import max
from mediacore.lib.filetypes import VIDEO
from mediacore.lib.i18n import N_, _
from mediacore.lib.storage.api import EmbedStorageEngine, UserStorageError
from mediacore.lib.uri import StorageURI

class YoutubeStorage(EmbedStorageEngine):

    engine_type = u'YoutubeStorage'
    """A uniquely identifying unicode string for the StorageEngine."""

    default_name = N_(u'YouTube')

    url_pattern = re.compile(r'''
        ^(http(s?)://)?                         # http:// or https://
        (youtu\.be/                             # youtu.be short url OR:
        |(\w+\.)?youtube\.com/watch\?(.*&)?v=   # www.youtube.com/watch?v= OR
        |(\w+\.)?youtube\.com/embed/)           # www.youtube.com/embed/ OR
        (?P<id>[^&#]+)                          # video unique ID
    ''', re.VERBOSE)
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

        yt_service = gdata.youtube.service.YouTubeService()
        yt_service.ssl = False

        try:
            entry = yt_service.GetYouTubeVideoEntry(video_id=id)
        except gdata.service.RequestError, request_error:
            e = request_error.args[0]
            if e['status'] == 403 and e['body'] == 'Private video':
                raise UserStorageError(
                    _('This video is private and cannot be embedded.'))
            elif e['status'] == 400 and e['body'] == 'Invalid id':
                raise UserStorageError(
                    _('Invalid YouTube URL. This video does not exist.'))
            raise UserStorageError(_('YouTube Error: %s') % e['body'])

        try:
            thumb = max(entry.media.thumbnail, key=attrgetter('width')).url
        except (AttributeError, ValueError, TypeError):
            # At least one video has been found to return no thumbnails.
            # Try adding this later http://www.youtube.com/watch?v=AQTYoRpCXwg
            thumb = None

        # Some videos at some times do not return a complete response, and these
        # attributes are missing. We can just ignore this.
        try:
            description = unicode(entry.media.description.text, 'utf-8') or None
        except (AttributeError, ValueError, TypeError, UnicodeDecodeError):
            description = None
        try:
            title = unicode(entry.media.title.text, 'utf-8')
        except (AttributeError, ValueError, TypeError, UnicodeDecodeError):
            title = None
        try:
            duration = int(entry.media.duration.seconds)
        except (AttributeError, ValueError, TypeError):
            duration = None

        return {
            'unique_id': id,
            'duration': duration,
            'display_name': title,
            'description': description,
            'thumbnail_url': thumb,
            'type': VIDEO,
        }

    def get_uris(self, media_file):
        """Return a list of URIs from which the stored file can be accessed.

        :type media_file: :class:`~mediacore.model.media.MediaFile`
        :param media_file: The associated media file object.
        :rtype: list
        :returns: All :class:`StorageURI` tuples for this file.

        """
        params = self._data.get('player_params', {})
        params = dict((k, int(v)) for k, v in params.iteritems())
        play_url = 'http://youtube%s.com/embed/%s?%s' % (
            self._data.get('nocookie', False) and '-nocookie' or '',
            media_file.unique_id,
            urlencode(params, True),
        )
        web_url = 'http://youtube.com/watch?v=%s' % media_file.unique_id
        return [
            StorageURI(media_file, 'youtube', play_url, None),
            StorageURI(media_file, 'www', web_url, None),
        ]

EmbedStorageEngine.register(YoutubeStorage)
