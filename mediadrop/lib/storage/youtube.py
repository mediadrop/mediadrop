# This file is a part of MediaDrop (http://www.mediadrop.video),
# Copyright 2009-2015 MediaDrop contributors
# For the exact contribution history, see the git revision log.
# The source code contained in this file is licensed under the GPLv3 or
# (at your option) any later version.
# See LICENSE.txt in the main project directory, for more information.

import re

from urllib import urlencode

from mediadrop.lib.i18n import _, N_
from mediadrop.lib.services import build_youtube_client
from mediadrop.lib.storage.api import EmbedStorageEngine, UserStorageError
from mediadrop.lib.uri import StorageURI


__all__ = ['YoutubeStorage']

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
        video_id = kwargs['id']
        youtube = build_youtube_client()
        if youtube is None:
            msg = _('No API key configured for YouTube (use Google\'s developer console to create one)')
            raise UserStorageError(msg)
        yt_result = youtube.fetch_video_details(video_id)
        if not yt_result:
            raise UserStorageError(yt_result.message)
        video_info = yt_result.meta_info.copy()
        video_info['thumbnail_url'] = yt_result.meta_info['thumbnail']['url']
        del video_info['thumbnail']
        return video_info

    def get_uris(self, media_file):
        """Return a list of URIs from which the stored file can be accessed.

        :type media_file: :class:`~mediadrop.model.media.MediaFile`
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
