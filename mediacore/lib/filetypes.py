import re
from pylons import config, request

__all__ = [
    'accepted_extensions',
    'embeddable_filetypes',
    'guess_media_type',
    'mimetype_lookup',
    'playable_types',
]

# Mimetypes
mimetype_lookup = {
    # TODO: Replace this with a more complete list.
    #       or modify code to detect mimetype from something other than ext.
    'm4a':  'audio/mpeg',
    'm4v':  'video/mpeg',
    'mp3':  'audio/mpeg',
    'mp4':  'audio/mpeg',
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

default_media_mimetype = 'application/octet-stream'

embeddable_filetypes = {
    'youtube': {
        'play': 'http://youtube.com/v/%s',
        'link': 'http://youtube.com/watch?v=%s',
        'pattern': re.compile('^(http(s?)://)?(www.)?youtube.com/watch\?(.*&)?v=(?P<id>[^&#]+)')
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

playable_types = {
    'audio': ('mp3', 'mp4', 'm4a'),
    'video': ('flv', 'm4v'),
    None: (),
}

flash_support = ('mp3', 'mp4', 'm4v', 'm4a', 'flv', 'f4v', 'f4p', 'f4a', 'f4b', 'flac')
upload_only_support = ('3gp', '3g2', 'divx', 'dv', 'dvx', 'mov', 'mpeg', 'mpg', 'vob', 'qt', 'wmv')
accepted_formats = set(flash_support)
accepted_formats.union(upload_only_support)
accepted_formats = sorted(accepted_formats)

# Container and Codec support for HTML5 tag in various browsers.
# The following list taken from http://diveintohtml5.org/video.html#what-works
# Safari also supports all default quicktime formats. But we'll keep it simple.
# h264 = h264 all profiles
# h264b = h264 baseline profile
# aac = aac all profiles
# aacl = aac low complexity profile
html5_support = {
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
    ],
    'safari': [
        (522, 'mp4', ['h264', 'aac']), # revision 522 was introduced in version 3.0
        (522, 'mp4', ['h264b', 'aacl']),
    ],
    'iphone': [
        (0, 'mp4', ['h264b', 'aacl']),
        # FIXME: Dirty hack to maximize chance of showing videos in iPhone.
        # Even though the iPhone can't actually handle full quality h264 and
        # AAC encodings, our system never knows for sure if the files are
        # baseline/low complexity or full quality. Even though the files are
        # likely not to work with HTML5 this way, they're guaranteed not to
        # work if we serve flash. So we lie, here, and hope for the best.
        (0, 'mp4', ['h264', 'aac']),
    ],
    'android': [
        (0, 'mp4', ['h264b', 'aacl']),
    ],
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
    html5_options = []
    for req_version, containers, codecs in html5_support.get(browser, []):
        if version >= req_version:
            html5_options.append((containers, codecs))
    return html5_options

def guess_media_type(container):
    if container in ('mp3', 'flac', 'f4a', 'm4a'):
        return 'audio'
    elif container in ('xml', 'srt'):
        return 'captions'
    return 'video'

def pick_media_file_player(files):
    """Return the best choice of files to play and which player to use.

    :param files: :class:`~mediacore.model.media.MediaFile` instances.
    :type files: list
    :rtype: tuple
    :returns: A :class:`~mediacore.model.media.MediaFile` and a player name.

    """
    from mediacore.lib.helpers import fetch_setting

    if fetch_setting('player_type') == 'best':
        for container, codecs in supported_html5_types():
            for file in files:
                if file.type in ('audio', 'video') \
                and file.container == container:
                    return file, fetch_setting('html5_player')

    for file in files:
        if file.type in ('audio', 'video') \
        and file.container in flash_support:
            return file, fetch_setting('flash_player')

    for file in files:
        if file.type in ('audio', 'video') \
        and file.container in embeddable_filetypes:
            return file, 'embed'

    return None, None

