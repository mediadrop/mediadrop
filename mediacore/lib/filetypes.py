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

__all__ = [
    'guess_container_format',
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

def guess_container_format(extension):
    """Return the most likely container format based on the file extension.

    This standardizes to an audio/video-agnostic form of the container, if
    applicable. For example m4v becomes mp4.

    :param extension: the file extension, without a preceding period.
    :type extension: string
    :rtype: string

    """
    mt = guess_mimetype(extension, default=True)
    if mt is True:
        return extension
    return container_lookup.get(mt)

def guess_media_type(extension=None, default=VIDEO):
    """Return the most likely media type based on the container or embed site.

    :param extension: The file extension without a preceding period.
    :param default: Default to video if we don't have any other guess.
    :returns: AUDIO, VIDEO, CAPTIONS, or None

    """
    return guess_media_type_map.get(extension, default)

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
