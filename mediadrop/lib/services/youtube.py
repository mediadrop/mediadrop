# -*- coding: UTF-8 -*-
# This file is a part of MediaDrop (http://www.mediadrop.video),
# Copyright 2009-2015 MediaDrop contributors
# For the exact contribution history, see the git revision log.
# The source code contained in this file is licensed under the GPLv3 or
# (at your option) any later version.
# See LICENSE.txt in the main project directory, for more information.

from __future__ import absolute_import, unicode_literals

import apiclient
import aniso8601
import simplejson as json
from webob.datetime_utils import timedelta_to_seconds

from mediadrop.lib.filetypes import VIDEO
from mediadrop.lib.i18n import _
from mediadrop.lib.result import Result


YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'


__all__ = ['build_youtube_client']

# Design idea: This file should be independent from the Google API client so
# it can be tested easily.
class YouTubeClient(object):
    def __init__(self, youtube):
        self.youtube = youtube

    def fetch_video_details(self, video_id):
        video_result = self._retrieve_video_details(video_id, 'snippet,contentDetails')
        # LATER: add debug logging for youtube response
        if video_result == False:
            return Result(
                False,
                meta_info=None,
                message=video_result.message
            )
        elif len(video_result) == 0:
            return Result(
                False,
                meta_info=None,
                message=_('Invalid YouTube URL. This video does not exist or is private and can not be embedded.')
            )
        video_details = video_result[0]
        iso8601_duration = video_details['contentDetails']['duration']
        duration = aniso8601.parse_duration(iso8601_duration)
        snippet = video_details['snippet']
        best_thumbnail = self._find_biggest_thumbnail(snippet['thumbnails'])
        meta_info = {
            'unique_id': video_details['id'],
            'duration': timedelta_to_seconds(duration),
            'display_name': snippet['title'],
            'description': snippet['description'],
            'thumbnail': {
                'width': best_thumbnail['width'],
                'height': best_thumbnail['height'],
                'url': best_thumbnail['url'],
            },
            'type': VIDEO,
        }
        return Result(True, meta_info=meta_info, message=None)

    def _find_biggest_thumbnail(self, thumbnails):
        # not all videos have the same thumbnails available so we actually need
        # to find the biggest one (to minimize jpeg artifacts due to rescaling).
        best = None
        for thumb_data in thumbnails.values():
            if best is None:
                best = thumb_data
            elif (best['width'] * best['height']) < (thumb_data['width'] * thumb_data['height']):
                best = thumb_data
        return best

    def fetch_views(self, video_id):
        videos = self._retrieve_video_details(video_id, 'statistics')
        if len(videos) == 0:
            return None
        video_item = videos[0]
        views = video_item['statistics']['viewCount']
        if not views:
            return None
        return int(views)

    def _retrieve_video_details(self, video_id, parts):
        search = self.youtube.videos().list(
            id=video_id,
            part=parts,
        )
        try:
            search_response = search.execute()
        except apiclient.errors.HttpError as api_error:
            response_content = api_error.content
            # LATER: log raw error content
            error_details = json.loads(response_content)['error']['errors'][0]
            reason = error_details['reason']
            youtube_reason = reason
            if 'message' in error_details:
                youtube_reason += ' / ' + error_details['message']
            message = _('unknown YouTube error: %(reason)s') % dict(reason=youtube_reason)
            if reason == 'keyInvalid':
                message = _('Invalid API key. Please check your Google API key in settings.')
            elif reason == 'accessNotConfigured':
                # Access Not Configured. The API (YouTube Data API) is not
                # enabled for your project. Please use the Google Developers
                # Console to update your configuration.
                message = error_details['message']
            return Result(False, message=message)
        videos = search_response.get('items', [])
        return videos


def build_youtube_client():
    google_developer_key = fetch_google_api_key()
    if google_developer_key is None:
        return None
    youtube = apiclient.discovery.build(
        YOUTUBE_API_SERVICE_NAME,
        YOUTUBE_API_VERSION,
        developerKey=google_developer_key
    )
    return YouTubeClient(youtube)

def fetch_google_api_key():
    # unfortunately the whole mediadrop.lib package is a bit convoluted leading
    # to some cyclic dependencies. model needs something from lib.storage
    # (which in turn likes to use this module). Just moving this one import here
    # is likely the least intrusive fix for this.
    from mediadrop.model import Setting
    key_config = Setting.query.filter(Setting.key == u'google_apikey').first()
    if not key_config:
        return None
    return key_config.value or None

