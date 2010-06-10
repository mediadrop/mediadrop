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
    'guess_container_format'
    'guess_media_type',
    'guess_mimetype',
    'parse_embed_url',
    'pick_media_file_player',
]

AUDIO = 'audio'
VIDEO = 'video'
CAPTIONS = 'captions'

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
    'flac': 'audio/flac',
    'mp3':  'audio/mpeg',
    'mp4':  '%s/mp4',
    'm4a':  'audio/mp4',
    'm4v':  'video/mp4',
    'ogg':  '%s/ogg',
    'oga':  'audio/ogg',
    'ogv':  'video/ogg',
    'mka':  'audio/x-matroska',
    'mkv':  'video/x-matroska',
    '3gp':  '%s/3gpp',
    '3g2':  '%s/3gpp',
    'avi':  'video/avi',
    'dv':   'video/x-dv',
    'flv':  'video/x-flv', # made up, it's what everyone uses anyway.
    'mov':  'video/quicktime',
    'mpeg': '%s/mpeg',
    'mpg':  '%s/mpeg',
    'wmv':  'video/x-ms-wmv',
    'xml':  'application/ttml+xml',
    'srt':  'text/plain',
}

# Default container format (and also file extension) for each mimetype we allow
# users to upload.
container_lookup = {
    'audio/flac': 'flac',
    'audio/mp4': 'mp4',
    'audio/mpeg': 'mp3',
    'audio/ogg': 'ogg',
    'audio/x-matroska': 'mka',
    'video/3gpp': '3gp',
    'video/avi': 'avi',
    'video/mp4': 'mp4',
    'video/mpeg': 'mpg',
    'video/ogg': 'ogg',
    'video/quicktime': 'mov',
    'video/x-dv': 'dv',
    'video/x-flv': 'flv',
    'video/x-matroska': 'mkv',
    'video/x-ms-wmv': 'wmv',
    'video/x-vob': 'vob',
    'application/ttml+xml': 'xml',
    'text/plain': 'srt',
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
    '3g2':  VIDEO,
    'avi':  VIDEO,
    'dv':   VIDEO,
    'flv':  VIDEO,
    'mov':  VIDEO,
    'mpeg': VIDEO,
    'mpg':  VIDEO,
    'wmv':  VIDEO,
    'xml':  CAPTIONS,
    'srt':  CAPTIONS,
}

# Patterns for embedding third party video which extract the video ID
external_embedded_containers = {
    'youtube': {
        'pattern': re.compile('^(http(s?)://)?(\w+.)?youtube.com/watch\?(.*&)?v=(?P<id>[^&#]+)'),
        'play': 'http://youtube.com/v/%s?rel=0&fs=1&hd=1',
        'link': 'http://youtube.com/watch?v=%s',
        'type': VIDEO,
    },
    'google': {
        'pattern': re.compile('^(http(s?)://)?video.google.com/videoplay\?(.*&)?docid=(?P<id>-?\d+)'),
        'play': 'http://video.google.com/googleplayer.swf?docid=%s&hl=en&fs=true',
        'link': 'http://video.google.com/videoplay?docid=%s',
        'type': VIDEO,
    },
    'vimeo': {
        'pattern': re.compile('^(http(s?)://)?(www.)?vimeo.com/(?P<id>\d+)'),
        'play': 'http://vimeo.com/moogaloop.swf?clip_id=%s&server=vimeo.com&show_title=1&show_byline=1&show_portrait=0&color=&fullscreen=1',
        'link': 'http://vimeo.com/%s',
        'type': VIDEO,
    },
}

# The list of file extensions that flash should recognize and be able to play.
flash_supported_containers = ['mp3', 'mp4', 'm4v', 'm4a', 'flv', 'flac']
flash_supported_browsers = ['firefox', 'opera', 'chrome', 'safari', 'unknown']

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
    ],
    'opera': [
        (10.5, 'ogg', ['theora', 'vorbis']),
    ],
    'chrome': [
        (3.0, 'ogg', ['theora', 'vorbis']),
        (3.0, 'mp4', ['h264', 'aac']),
        (3.0, 'm4v', ['h264', 'aac']),
        (3.0, 'm4a', []),
        (3.0, 'mp3', []),
    ],
    'safari': [
        (522, 'mp4', ['h264', 'aac']), # revision 522 was introduced in version 3.0
        (522, 'm4v', ['h264', 'aac']),
        (522, 'm4a', []),
        (522, 'mp3', []),
    ],
    'itunes': [
        (0, 'mp4', ['h264', 'aac']),
        (0, 'm4v', ['h264', 'aac']),
        (0, 'm4a', []),
        (0, 'mp3', []),
    ],
    'iphone-ipod-ipad': [
        (0, 'mp4', ['h264b', 'aacl']),
        (0, 'm4v', ['h264b', 'aacl']),
        (0, 'm4a', []),
        (0, 'mp3', []), # TODO: Test this. We assume it is supported because Safari supports it.
    ],
    'android': [
        (0, 'mp4', ['h264b', 'aacl']),
        (0, 'm4v', ['h264b', 'aacl']),
        (0, 'm4a', []),
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

def accepted_extensions():
    """Return the extensions allowed for upload.

    :rtype: list
    """
    e = mimetype_lookup.keys()
    e.sort()
    return e

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
            return {
                'container': container,
                'id': match.group('id'),
                'type': info['type'],
            }
    return None

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
    :returns: 'audio', 'video', 'captions', or None

    """
    if extension is not None:
        return guess_media_type_map.get(extension, default)
    if embed is not None:
        return external_embedded_containers.get(embed, {}).get('type', default)
    return default

def guess_mimetype(container, type_=None, default=None):
    """Return the best guess mimetype for the given container.

    If the type (audio or video) is not provided, we make our best guess
    as to which is will probably be, using :func:`guess_container_type`.
    Note that this value is ignored for certain mimetypes: it's useful
    only when a container can be both audio and video.

    :param container: The file extension
    :param type_: 'audio', 'video' or 'captions'
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

def pick_media_file_player(files, browser=None, version=None, user_agent=None,
        player_type=None, include_embedded=True):
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
    :param browser: Optional browser name to bypass user agents altogether.
        See :attr:`native_browser_supported_containers` for possible values.
    :type browser: str or None
    :param version: Optional version number, used when a browser arg is given.
    :type version: float or None
    :param user_agent: Optional User-Agent header to use. Defaults to
        that of the current request.
    :type user_agent: str or None
    :param player_type: Optional override value for the player_type setting.
    :type player_type: str or None
    :param include_embedded: Whether or not to include embedded players.
    :type include_embedded: bool
    :returns: A :class:`~mediacore.model.media.MediaFile` object or None,
        a :class:`~mediacore.lib.helpers.Player` object or None,
        the detected browser name, and the detected browser version.
    :rtype: tuple

    """
    from mediacore.lib.helpers import fetch_setting, players

    def get_html5_player():
        for container, codecs in native_supported_types(browser, version):
            for file in files:
                if file.container == container:
                    return file, players.get(html5_player, html5_player)
        return None, None

    def get_flash_player():
        if browser in flash_supported_browsers:
            for file in files:
                if file.container in flash_supported_containers:
                    return file, players.get(flash_player, flash_player)
        return None, None

    def get_embedded_player():
        for file in files:
            if file.container in external_embedded_containers:
                return file, players[file.container]
        return None, None

    if browser is None:
        browser, version = parse_user_agent_version(user_agent)

    if player_type is None:
        player_type = fetch_setting('player_type')

    html5_player = fetch_setting('html5_player')
    flash_player = fetch_setting('flash_player')

    # Only proceed if this file is a playable type
    files = [file for file in files if file.type in (AUDIO, VIDEO)]

    file, player = None, None
    ef_file, ef_player = None, None
    eh_file, eh_player = None, None

    if player_type == 'html5':
        file, player = get_html5_player()

    elif player_type == 'best':
        # Prefer embedded videos with a HTML5 player
        # FIXME: Ignores client browser support for HTML5.
        if include_embedded:
            file, player = get_embedded_player()
            if player is not None and not player.is_html5:
                ef_file, ef_player = file, player
                file, player = None, None

        # Fall back to hosted videos with an HTML5 player
        if player is None:
            file, player = get_html5_player()

        # Fall back to embedded videos with a Flash player
        if player is None \
        and include_embedded \
        and browser in flash_supported_browsers:
            file, player = ef_file, ef_player

        # Fall back to hosted videos with a Flash player
        if player is None:
            file, player = get_flash_player()

        # Fall back to embedded videos with a Flash player, even if the
        # client browser doesn't support Flash. This ignorance is a last ditch
        # effort to allow devices to specially handle YouTube, Vimeo, et al.
        # e.g. It allows iPhones to display YouTube videos.
        if player is None and include_embedded:
            file, player = ef_file, ef_player

    elif player_type == 'flash':
        ef_file, ef_player = None, None

        # Prefer embedded videos with a Flash player
        if include_embedded:
            file, player = get_embedded_player()
            if player is not None:
                if player.is_flash and browser not in flash_supported_browsers:
                    ef_file, ef_player = file, player
                    file, player = None, None
                elif not player.is_flash:
                    eh_file, eh_player = file, player
                    file, player = None, None

        # Fall back to hosted videos with a Flash player
        if player is None:
            file, player = get_flash_player()

        # Fall back to embedded videos with an HTML5 player
        # FIXME: Ignores client browser support for HTML5.
        if player is None and include_embedded:
            file, player = eh_file, eh_player

        # Fall back to hosted videos with an HTML5 player
        if player is None:
            file, player = get_html5_player()

        # Fall back to embedded videos with a Flash player, even if the
        # client browser doesn't support Flash. This ignorance is a last ditch
        # effort to allow devices to specially handle YouTube, Vimeo, et al.
        # e.g. It allows iPhones to display YouTube videos.
        if player is None and include_embedded:
            file, player = ef_file, ef_player

    return file, player, browser, version
