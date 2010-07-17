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
from pylons import request

__all__ = [
    'accepted_extensions',
    'guess_container_format'
    'guess_media_type',
    'guess_mimetype',
]

AUDIO = u'audio'
VIDEO = u'video'
AUDIO_DESC = u'audio_desc'
CAPTIONS = u'captions'

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
# XXX: This list can contain at most 21 items! Any more will crash Flash when
#      accepted_extensions() is passed to Swiff.Uploader to provide the
#      typeFilter.
mimetype_lookup = {
    u'flac': u'audio/flac',
    u'mp3':  u'audio/mpeg',
    u'mp4':  u'%s/mp4',
    u'm4a':  u'audio/mp4',
    u'm4v':  u'video/mp4',
    u'ogg':  u'%s/ogg',
    u'oga':  u'audio/ogg',
    u'ogv':  u'video/ogg',
    u'mka':  u'audio/x-matroska',
    u'mkv':  u'video/x-matroska',
    u'3gp':  u'%s/3gpp',
    u'avi':  u'video/avi',
    u'dv':   u'video/x-dv',
    u'flv':  u'video/x-flv', # made up, it's what everyone uses anyway.
    u'mov':  u'video/quicktime',
    u'mpeg': u'%s/mpeg',
    u'mpg':  u'%s/mpeg',
    u'webm': u'%s/webm',
    u'wmv':  u'video/x-ms-wmv',
    u'xml':  u'application/ttml+xml',
    u'srt':  u'text/plain',
}

# Default container format (and also file extension) for each mimetype we allow
# users to upload.
container_lookup = {
    u'audio/flac': u'flac',
    u'audio/mp4': u'mp4',
    u'audio/mpeg': u'mp3',
    u'audio/ogg': u'ogg',
    u'audio/x-matroska': u'mka',
    u'audio/webm': u'webm',
    u'video/3gpp': u'3gp',
    u'video/avi': u'avi',
    u'video/mp4': u'mp4',
    u'video/mpeg': u'mpg',
    u'video/ogg': u'ogg',
    u'video/quicktime': u'mov',
    u'video/x-dv': u'dv',
    u'video/x-flv': u'flv',
    u'video/x-matroska': u'mkv',
    u'video/x-ms-wmv': u'wmv',
    u'video/x-vob': u'vob',
    u'video/webm': u'webm',
    u'application/ttml+xml': u'xml',
    u'text/plain': u'srt',
}

# When media_obj.container doesn't match a key in the mimetype_lookup dict...
default_media_mimetype = 'application/octet-stream'

# File extension map to audio, video or captions
guess_media_type_map = {
    'mp3':  AUDIO,
    'm4a':  AUDIO,
    'flac': AUDIO,
    'mp4':  VIDEO,
    'm4v':  VIDEO,
    'ogg':  VIDEO,
    'oga':  AUDIO,
    'ogv':  VIDEO,
    'mka':  AUDIO,
    'mkv':  VIDEO,
    '3gp':  VIDEO,
    'avi':  VIDEO,
    'dv':   VIDEO,
    'flv':  VIDEO,
    'mov':  VIDEO,
    'mpeg': VIDEO,
    'mpg':  VIDEO,
    'webm': VIDEO,
    'wmv':  VIDEO,
    'xml':  CAPTIONS,
    'srt':  CAPTIONS,
}

# The list of file extensions that flash should recognize and be able to play.
flash_supported_containers = ['mp3', 'mp4', 'm4v', 'm4a', 'flv', 'flac']
flash_supported_browsers = ['firefox', 'opera', 'chrome', 'safari', 'android', 'unknown']

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
#        Furthermore, the list of codec support is very incomplete.
# XXX: not all container types here will be be considered playable by the
#      system, as the associated media files will not be marked 'encoded' as
#      per the playable_containers dict.
native_supported_containers_codecs = {
    'firefox': [
        (3.5, 'ogg', ['theora', 'vorbis']),
        (4.0, 'webm', ['vp8', 'vorbis']),
    ],
    'opera': [
        (10.5, 'ogg', ['theora', 'vorbis']),
        (10.6, 'webm', ['vp8', 'vorbis']),
    ],
    'chrome': [
        (3.0, 'ogg', ['theora', 'vorbis']),
        (3.0, 'mp4', ['h264', 'aac']),
        (3.0, 'mp3', []),
        (6.0, 'webm', ['vp8', 'vorbis']), # XXX: Support was actually added in 6.0.453.1, WebKit 534
    ],
    'safari': [
        (522, 'mp4', ['h264', 'aac']), # revision 522 was introduced in version 3.0
        (522, 'mp3', []),
    ],
    'itunes': [
        (0, 'mp4', ['h264', 'aac']),
        (0, 'mp3', []),
    ],
    'iphone-ipod-ipad': [
        (0, 'mp4', ['h264b', 'aacl']),
        (0, 'mp3', []), # TODO: Test this. We assume it is supported because Safari supports it.
    ],
    'android': [
        (0, 'mp4', ['h264b', 'aacl']),
        (0, 'mp3', []), # TODO: Test this. We assume it is supported because Chrome supports it.
    ],
    'unknown': [],
}

# This is a wildly incomplete set of regular expressions that parse the
# important numbers from the browser version for determining things like
# HTML5 support.
user_agent_regexes = (
    # chrome UA contains the safari UA string. check for chrome before safari
    ('chrome', re.compile(r'Chrome.(\d+\.\d+)')),
    # iphone-ipod-ipad UA contains the safari UA string. check for iphone-ipod-ipad before safari
    ('iphone-ipod-ipad', re.compile(r'i(?:Phone|Pod|Pad).+Safari/(\d+\.\d+)')),
    ('firefox', re.compile(r'Firefox.(\d+\.\d+)')),
    ('opera', re.compile(r'Opera.(\d+\.\d+)')),
    ('safari', re.compile(r'Safari.(\d+\.\d+)')),
    ('android', re.compile(r'Android.(\d+\.\d+)')),
    ('itunes', re.compile(r'iTunes/(\d+\.\d+)')),
)

def accepted_extensions(*types):
    """Return the extensions allowed for upload.

    Limit to certain file types like so::

        audio_video_exts = accepted_extensions('audio', 'video')

    :rtype: list
    """
    if types:
        e = [e for e, t in guess_media_type_map.iteritems() if t in types]
    else:
        e = guess_media_type_map.keys()
    e.sort()
    return e

def parse_user_agent_version(ua=None):
    """Return a tuple representing the user agent's browser name and version.

    :param ua: An optional User-Agent header to use. Defaults to
        that of the current request.
    :type ua: str

    """
    if ua is None:
        ua = request.headers.get('User-Agent', '')
    for device, pattern in user_agent_regexes:
        match = pattern.search(ua)
        if match is not None:
            version = float(match.groups()[0])
            return device, version
    return 'unknown', 0

def native_supported_types(browser, version=None):
    """Return the browser's supported HTML5 video containers and codecs.

    The browser can be determined automatically from the user agent. If
    no browser and no user agent is specified, the user agent is read
    from the request headers. See :func

    :param browser: Browser name from :attr:`native_browser_supported_containers`
    :type browser: str or None
    :param version: Optional version number, used when a browser arg is given.
    :type version: float or None
    :returns: The containers and codecs supported by the given browser/version.
    :rtype: list

    """
    if browser not in native_supported_containers_codecs:
        browser = 'unknown'
    scc = native_supported_containers_codecs[browser]
    native_options = []

    for req_version, containers, codecs in scc:
        if version is None or version >= req_version:
            native_options.append((containers, codecs))
    return native_options

def guess_container_format(extension):
    """Return the most likely container format based on the file extension.

    This standardizes to an audio/video-agnostic form of the container, if
    applicable. For example m4v becomes mp4.

    :param extension: the file extension, without a preceding period.
    :type extension: string
    :rtype: string or None

    """
    mt = guess_mimetype(extension)
    return container_lookup.get(mt, None)

def guess_media_type(extension=None, embed=None, default=VIDEO):
    """Return the most likely media type based on the container or embed site.

    :param extension: Optional, the file extension without a preceding period.
    :param embed: Optional, the third-party site name.
    :param default: Default to video if we don't have any other guess.
    :returns: AUDIO, VIDEO, CAPTIONS, or None

    """
    if extension is not None:
        return guess_media_type_map.get(extension, default)
    if embed is not None:
        from mediacore.lib.embedtypes import external_embedded_containers
        return external_embedded_containers.get(embed, {}).get('type', default)
    return default

def guess_mimetype(container, type_=None, default=None):
    """Return the best guess mimetype for the given container.

    If the type (audio or video) is not provided, we make our best guess
    as to which is will probably be, using :func:`guess_container_type`.
    Note that this value is ignored for certain mimetypes: it's useful
    only when a container can be both audio and video.

    :param container: The file extension
    :param type_: AUDIO, VIDEO, or CAPTIONS
    :param default: Default mimetype for when guessing fails
    :returns: A mime string or None.

    """
    if type_ is None:
        type_ = guess_media_type(container)
    mt = mimetype_lookup.get(container, None)
    if mt is None:
        return default or default_media_mimetype
    try:
        return mt % type_
    except (ValueError, TypeError):
        return mt
