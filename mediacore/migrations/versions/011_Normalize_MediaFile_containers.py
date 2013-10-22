# This file is a part of MediaDrop (http://www.mediadrop.net),
# Copyright 2009-2013 MediaCore Inc., Felix Schwarz and other contributors.
# For the exact contribution history, see the git revision log.
# The source code contained in this file is licensed under the GPLv3 or
# (at your option) any later version.
# See LICENSE.txt in the main project directory, for more information.

"""
A script to standardize file containers to their preferred container formats.

This changes MediaFile.container and MediaFile.display_name, but leaves the
internal MediaFile.file_name intact, so that we don't need to move files
around.
"""
import logging
import os.path
from datetime import datetime
from sqlalchemy import *
from migrate import *

log = logging.getLogger(__name__)

metadata = MetaData()
media_files = Table('media_files', metadata,
    Column('id', Integer, autoincrement=True, primary_key=True),
    Column('media_id', Integer, ForeignKey('media.id', onupdate='CASCADE', ondelete='CASCADE'), nullable=False),

    Column('type', Enum('video', 'audio', 'audio_desc', 'captions', name='type'), nullable=False),
    Column('container', String(10), nullable=False),
    Column('display_name', String(255), nullable=False),
    Column('file_name', String(255)),
    Column('url', String(255)),
    Column('embed', String(50)),
    Column('size', Integer),

    Column('created_on', DateTime, default=datetime.now, nullable=False),
    Column('modified_on', DateTime, default=datetime.now, onupdate=datetime.now, nullable=False),

    mysql_engine='InnoDB',
    mysql_charset='utf8',
)

def upgrade(migrate_engine):
    metadata.bind = migrate_engine
    conn = migrate_engine.connect()
    transaction = conn.begin()
    try:
        normalize_containers(conn)
        transaction.commit()
    except:
        transaction.rollback()
        raise

def downgrade(migrate_engine):
    pass

def normalize_containers(conn):
    query = select([
        media_files.c.id,
        media_files.c.container,
        media_files.c.file_name,
        media_files.c.display_name,
    ])
    changes = []
    for file_id, container, file_name, display_name in conn.execute(query):
        if not file_name:
            # This change only applies to locally hosted files
            continue
        new_container = guess_container_format(container)
        if new_container is None:
            log.warning('File ID %d contains an unknown container: "%s"' % (file_id, container))
            continue
        name, orig_ext = os.path.splitext(display_name)
        if new_container != orig_ext.lstrip('.') \
        or new_container != container:
            changes.append({
                'file_id': file_id,
                'container': new_container,
                'name': '%s.%s' % (name, new_container),
            })
    if changes:
        update = media_files.update().where(media_files.c.id==bindparam('file_id'))\
                                     .values(container=bindparam('container'),
                                             display_name=bindparam('name'))
        conn.execute(update, *changes)

# Copy of all code needed for mediacore.lib.filetypes.guess_container_format
# Copied, not imported, so that this script will work even if this function
# is removed down the road.

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

def guess_media_type(extension=None, embed=None, default=VIDEO):
    """Return the most likely media type based on the container or embed site.

    :param extension: Optional, the file extension without a preceding period.
    :param embed: Optional, the third-party site name.
    :param default: Default to video if we don't have any other guess.
    :returns: 'audio', 'video', 'captions', or None

    """
    if extension is not None:
        return guess_media_type_map.get(extension, default)
#    if embed is not None:
#        return external_embedded_containers.get(embed, {}).get('type', default)
    return default
