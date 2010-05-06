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
from pylons import config, request

__all__ = [
    'accepted_extensions',
    'external_embedded_containers',
    'guess_container_format'
    'guess_media_type',
    'mimetype_lookup',
    'playable_containers',
]

# Mimetypes for all file extensions accepted by the front and backend uploaders
#
# OTHER USES:
# 1) To determine the mimetype to serve, based on a MediaFile's container type.
# 2) In conjunction with the container_lookup dict below to determine the
#    container type for a MediaFile, based on the uploaded file's extension.
#
# XXX: The keys in this dict are sometimes treated as names for container types
#      and sometimes treated as file extensions. Caveat coder.
# TODO: Replace with a more complete list or (even better) change the logic
#       to detect mimetypes from something other than the file extension.
mimetype_lookup = {
    'm4a':  'audio/mp4',
    'm4v':  'video/mp4',
    'mp3':  'audio/mpeg',
    'mp4':  'audio/mp4', # This is not strictly true. It could contain video.
    'flac': 'audio/flac',
    '3gp':  'video/3gpp',
    '3g2':  'video/3gpp',
    'divx': 'video/mpeg',
    'dv':   'video/x-dv',
    'dvx':  'video/mpeg',
    'flv':  'video/x-flv', # made up, it's what everyone uses anyway.
    'mov':  'video/quicktime',
    'mpeg': 'video/mpeg',
    'mpg':  'video/mpeg',
    'qt':   'video/quicktime',
    'vob':  'video/x-vob', # multiplexed container format
    'wmv':  'video/x-ms-wmv',
}

# Default container format (and also file extension) for each mimetype we allow
# users to upload.
container_lookup = {
    'audio/flac':      'flac',
    'audio/mp4':       'm4a',
    'audio/mpeg':      'mp3',
    'video/3gpp':      '3gp',
    'video/mp4':       'm4v',
    'video/mpeg':      'mpg',
    'video/quicktime': 'mov',
    'video/x-dv':      'dv',
    'video/x-flv':     'flv',
    'video/x-ms-wmv':  'wmv',
    'video/x-vob':     'vob',
}

# When media_obj.container doesn't match a key in the mimetype_lookup dict...
default_media_mimetype = 'application/octet-stream'

external_embedded_containers = {
    'youtube': {
        'play': 'http://youtube.com/v/%s',
        'link': 'http://youtube.com/watch?v=%s',
        'pattern': re.compile('^(http(s?)://)?(\w+.)?youtube.com/watch\?(.*&)?v=(?P<id>[^&#]+)')
    },
    'google': {
        'play': 'http://video.google.com/googleplayer.swf?docid=%s&hl=en&fs=true',
        'link': 'http://video.google.com/videoplay?docid=%s',
        'pattern': re.compile('^(http(s?)://)?video.google.com/videoplay\?(.*&)?docid=(?P<id>-\d+)')
    },
    'vimeo': {
        'play': 'http://vimeo.com/moogaloop.swf?clip_id=%s&server=vimeo.com&show_title=1&show_byline=1&show_portrait=0&color=&fullscreen=1',
        'link': 'http://vimeo.com/%s',
        'pattern': re.compile('^(http(s?)://)?(www.)?vimeo.com/(?P<id>\d+)')
    },
}

# The container types that will be considered to be 'encoded', and thus ready
# for playing, when they are uploaded.
playable_containers = {
    'audio': ('mp3', 'mp4', 'm4a'),
    'video': ('flv', 'mp4', 'm4v'),
    None: (),
}

# The list of file extensions that flash should recognize and be able to play.
# XXX: not all files with extensions matched here will be considered playable,
#      as the associated media files may not be considered 'encoded' as per the
#      playable_containers dict.
flash_supported_containers = ('mp3', 'mp4', 'm4v', 'm4a', 'flv', 'f4v', 'f4p', 'f4a', 'f4b', 'flac')

# Container and Codec support for HTML5 tag in various browsers.
# The following list taken from http://diveintohtml5.org/video.html#what-works
# Safari also supports all default quicktime formats. But we'll keep it simple.
# h264 = h264 all profiles
# h264b = h264 baseline profile
# aac = aac all profiles
# aacl = aac low complexity profile
# FIXME: While included for future usefuleness, the codecs in the list below
#        are ignored by the actual logic in pick_media_file_player() below.
#        If the media file in question has a container type that /might/ hold
#        a supported codec for the platform, we assume it will work.
# XXX: not all container types here will be be considered playable by the
#      system, as the associated media files will not be marked 'encoded' as
#      per the playable_containers dict.
html5_supported_containers_codecs = {
    'firefox': [
        (3.5, 'ogg', ['theora', 'vorbis']),
    ],
    'opera': [
        (10.5, 'ogg', ['theora', 'vorbis']),
    ],
    'chrome': [
        (3.0, 'ogg', ['theora', 'vorbis']),
        (3.0, 'mp4', ['h264', 'aac']),
        (3.0, 'mp4', ['h264b', 'aacl']),
        (3.0, 'm4v', ['h264', 'aac']),
        (3.0, 'm4v', ['h264b', 'aacl']),
    ],
    'safari': [
        (522, 'mp4', ['h264', 'aac']), # revision 522 was introduced in version 3.0
        (522, 'mp4', ['h264b', 'aacl']),
        (522, 'm4v', ['h264', 'aac']),
        (522, 'm4v', ['h264b', 'aacl']),
    ],
    'iphone': [
        (0, 'mp4', ['h264b', 'aacl']),
        (0, 'm4v', ['h264b', 'aacl']),
    ],
    'android': [
        (0, 'mp4', ['h264b', 'aacl']),
        (0, 'm4v', ['h264b', 'aacl']),
    ],
    'unknown': []
}

# This is a wildly incomplete set of regular expressions that parse the
# important numbers from the browser version for determining things like
# HTML5 support.
user_agent_regexes = {
    'chrome': re.compile(r'Chrome.(\d+\.\d+)'), # contains the safari string. check for chrome before safari
    'firefox': re.compile(r'Firefox.(\d+\.\d+)'),
    'opera': re.compile(r'Opera.(\d+\.\d+)'),
    'safari': re.compile(r'Safari.(\d+\.\d+)'),
    'android':  re.compile(r'Android.(\d+\.\d+)'),
    'iphone': re.compile(r'iPhone.+Safari/(\d+\.\d+)'),
}

def accepted_extensions():
    """Return the extensions allowed for upload.

    :rtype: list
    """
    e = mimetype_lookup.keys()
    e = sorted(e)
    return e

def parse_user_agent_version():
    """Return a tuple representing the user agent's browser name and version.
    """
    ua = request.headers.get('User-Agent', '')
    for device, pattern in user_agent_regexes.iteritems():
        match = pattern.search(ua)
        if match is not None:
            version = float(match.groups()[0])
            return device, version
    return 'unknown', 0

def supported_html5_types():
    """Return the user agent's supported HTML5 video containers and codecs.
    """
    browser, version = parse_user_agent_version()
    scc = html5_supported_containers_codecs[browser]
    html5_options = []

    for req_version, containers, codecs in scc:
        if version >= req_version:
            html5_options.append((containers, codecs))
    return html5_options

def guess_container_format(extension):
    """Return the most likely container format based on the file extension.

    :param extension: the file extension, without a preceding period.
    :type extension: string
    :rtype: string or None
    """
    try:
        mt = mimetype_lookup[extension]
        cf = container_lookup[mt]
        return cf
    except KeyError:
        return None

def guess_media_type(container):
    """Return the most likely media type based on the container format.
    """
    if container in ('mp3', 'flac', 'f4a', 'm4a'):
        return 'audio'
    elif container in ('xml', 'srt'):
        return 'captions'
    return 'video'

def pick_media_file_player(files):
    """Return the best choice of files to play and which player to use.

    XXX: This method uses the very unsophisticated technique of assuming
         that if the client is capable of playing the container format, then
         the client should be able to play the tracks within the container,
         regardless of the codecs actually used. As such, admins would be
         well advised to use the lowest-common-denominator for their targeted
         clients when using files for consumption in an HTML5 player, and
         to use the standard codecs when encoding for Flash player use.

    :param files: :class:`~mediacore.model.media.MediaFile` instances.
    :type files: list
    :rtype: tuple
    :returns: A :class:`~mediacore.model.media.MediaFile` and a player name.

    """
    from mediacore.lib.helpers import fetch_setting
    player_type = fetch_setting('player_type')

    # Only proceed if this file is a playable type
    files = [file for file in files if file.type in ('audio', 'video')]

    # First, check if it's an embedded video from another site.
    for file in files:
        if file.container in external_embedded_containers:
            return file, 'embed'

    # If possible, return an applicable file and html5 player
    # Note that this is currently based only on the container type
    if player_type in ['best', 'html5']:
        for container, codecs in supported_html5_types():
            for file in files:
                if file.container == container:
                    return file, fetch_setting('html5_player')

    # If possible, return an applicable file and flash player
    if player_type in ['best', 'flash']:
        for file in files:
            if file.container in flash_supported_containers:
                return file, fetch_setting('flash_player')

    # No acceptable file/player combination could be found.
    return None, None
