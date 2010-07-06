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
import simplejson
import shutil
import urllib2

import gdata.youtube
import gdata.youtube.service

from mediacore import __version__ as VERSION
from mediacore.lib.compat import max
from mediacore.lib.filetypes import AUDIO, VIDEO, AUDIO_DESC, CAPTIONS

__all__ = ['parse_embed_url']

def get_embed_details_youtube(id):
    """Given a YouTube video ID, return the associated thumbnail URL and
    the duration of the video.

    :param id: a valid YouTube video ID
    :type id: string
    :returns: Thumbnail URL (or None), and duration (or None)
    :rtype: tuple (string, int)
    """
    yt_service = gdata.youtube.service.YouTubeService()
    yt_service.ssl = False
    entry = yt_service.GetYouTubeVideoEntry(video_id=id)
    duration = int(entry.media.duration.seconds)
    tn = max(entry.media.thumbnail, key=lambda tn: int(tn.width))
    thumb_url = tn.url

    return thumb_url, duration

google_image_rgx = re.compile(r'media:thumbnail url="([^"]*)"')
google_duration_rgx = re.compile(r'duration="([^"]*)"')
def get_embed_details_google(id):
    """Given a Google Video ID, return the associated thumbnail URL and
    the duration of the video.

    :param id: a valid Google Video ID
    :type id: string
    :returns: Thumbnail URL (or None), and duration (or None)
    :rtype: tuple (string, int)
    """
    google_data_url = 'http://video.google.com/videofeed?docid=%s' % id
    thumb_url = None
    duration = None
    from mediacore.lib.helpers import decode_entities
    try:
        temp_data = urllib2.urlopen(google_data_url)
        data = temp_data.read()
        temp_data.close()
        thumb_match = google_image_rgx.search(data)
        dur_match = google_duration_rgx.search(data)
        if thumb_match:
            thumb_url = decode_entities(thumb_match.group(1))
        if dur_match:
            duration = int(dur_match.group(1))
    except urllib2.URLError, e:
        log.exception(e)

    return thumb_url, duration

def get_embed_details_vimeo(id):
    """Given a Vimeo video ID, return the associated thumbnail URL and
    the duration of the video.

    :param id: a valid Vimeo video ID
    :type id: string
    :returns: Thumbnail URL (or None), and duration (or None)
    :rtype: tuple (string, int)
    """
    # Vimeo API requires us to give a user-agent, to avoid 403 errors.
    headers = {
        'User-Agent': 'MediaCore %s' % VERSION,
    }
    vimeo_data_url = 'http://vimeo.com/api/v2/video/%s.%s' % (id, 'json')
    req = urllib2.Request(vimeo_data_url, headers=headers)
    thumb_url = None
    duration = None
    try:
        temp_data = urllib2.urlopen(req)
        data = simplejson.loads(temp_data.read())
        temp_data.close()
        thumb_url = data[0]['thumbnail_large']
        duration = int(data[0]['duration'])
    except urllib2.URLError, e:
        log.exception(e)

    return thumb_url, duration

# Patterns for embedding third party video which extract the video ID
external_embedded_containers = {
    'youtube': {
        'pattern': re.compile('^(http(s?)://)?(\w+.)?youtube.com/watch\?(.*&)?v=(?P<id>[^&#]+)'),
        'play': 'http://youtube.com/v/%s?rel=0&fs=1&hd=1',
        'link': 'http://youtube.com/watch?v=%s',
        'get_details': get_embed_details_youtube,
        'type': VIDEO,
    },
    'google': {
        'pattern': re.compile('^(http(s?)://)?video.google.com/videoplay\?(.*&)?docid=(?P<id>-?\d+)'),
        'play': 'http://video.google.com/googleplayer.swf?docid=%s&hl=en&fs=true',
        'link': 'http://video.google.com/videoplay?docid=%s',
        'get_details': get_embed_details_google,
        'type': VIDEO,
    },
    'vimeo': {
        'pattern': re.compile('^(http(s?)://)?(www.)?vimeo.com/(?P<id>\d+)'),
        'play': 'http://vimeo.com/moogaloop.swf?clip_id=%s&server=vimeo.com&show_title=1&show_byline=1&show_portrait=0&color=&fullscreen=1',
        'link': 'http://vimeo.com/%s',
        'get_details': get_embed_details_vimeo,
        'type': VIDEO,
    },
}

def parse_embed_url(url):
    """Parse the URL to return relevant info if its a for valid embed.

    :param url: A fully qualified URL.
    :returns: The container (embed site name), the unique id,
        and a type (audio or video).
    :rtype: dict or None

    """
    for container, info in external_embedded_containers.iteritems():
        match = info['pattern'].match(url)
        if match is not None:
            thumb_url, duration = info['get_details'](match.group('id'))
            return {
                'container': container,
                'id': match.group('id'),
                'type': info['type'],
                'thumb_url': thumb_url,
                'duration': duration,
            }
    return None
