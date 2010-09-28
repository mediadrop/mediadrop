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

import logging
import os
import re

from cStringIO import StringIO
from shutil import copyfileobj
from urllib2 import URLError, urlopen

from formencode import Invalid
from pylons import app_globals
from pylons.i18n import _

from mediacore.lib.decorators import memoize
from mediacore.lib.filetypes import guess_container_format, guess_media_type
from mediacore.lib.thumbnails import (create_thumbs_for, has_thumbs,
    has_default_thumbs, thumb_path)
from mediacore.plugin.abc import AbstractClass, abstractmethod, abstractproperty

__all__ = ['add_new_media_file']

log = logging.getLogger(__name__)


class StorageError(Exception):
    """Base class for all storage exceptions."""

class UnsuitableEngineError(StorageError):
    """Error to indicate that StorageEngine.parse can't parse its input."""


class StorageURI(object):
    """
    An access point for a :class:`mediacore.model.media.MediaFile`.

    A single file may be accessed in several different ways. Each `StorageURI`
    represents one such access point.

    .. attribute:: file

        The :class:`mediacore.model.media.MediaFile` this URI points to.

    .. attribute:: scheme

        The protocol, URI scheme, or other internally meaningful
        string. Don't be fooled into thinking this is always going to be
        the URI scheme (such as "rtmp://..") -- it may differ.

        Some examples include:
            * http
            * rtmp
            * youtube
            * www

    .. attribute:: file_uri

        The file-specific portion of the URI. In the case of
        HTTP URLs, for example, this will include the entire URL. Only
        when the server must be defined separately does this not include
        the entire URI.

    .. attribute:: server_uri

        An optional server URI. This is useful for RTMP
        streaming servers and the like, where a streaming server must
        be declared separately from the file.

    """
    __slots__ = ('file', 'scheme', 'file_uri', 'server_uri', '__weakref__')

    def __init__(self, file, scheme, file_uri, server_uri=None):
        self.file = file
        self.scheme = scheme
        self.file_uri = file_uri
        self.server_uri = server_uri

    def __str__(self):
        """Return the best possible string representation of the URI.

        NOTE: This string may not actually be usable for playing back
              certain kinds of media. Be careful with RTMP URIs.

        """
        if self.server_uri is not None:
            return os.path.join(self.server_uri, self.file_uri)
        return self.file_uri

    def __unicode__(self):
        return unicode(self.__str__())

    def __repr__(self):
        return "<StorageURI '%s'>" % self.__str__()

    def __getattr__(self, name):
        """Return attributes from the file as if they were defined on the URI.

        This method is called when an attribute lookup fails on this StorageURI
        instance. Before throwing an AttributeError, we first try the lookup
        on our :class:`~mediacore.model.media.MediaFile` instance.

        For example::

            self.scheme          # an attribute of this StorageURI
            self.file.container  # clearly an attribute of the MediaFile
            self.container       # the same attribute of the MediaFile

        :param name: Attribute name
        :raises AttributeError: If the lookup fails on the file.

        """
        if hasattr(self.file, name):
            return getattr(self.file, name)
        raise AttributeError('%r has no attribute %r, nor does the file '
                             'it contains.' % (self.__class__.__name__, name))


class StorageEngine(AbstractClass):
    """
    Base class for all Storage Engine implementations.
    """

    engine_type = abstractproperty()
    """A unique identifying unicode string for the StorageEngine."""

    default_name = abstractproperty()
    """A user-friendly display name that identifies this StorageEngine."""

    is_singleton = abstractproperty()

    settings_form_class = None
    """Your :class:`mediacore.forms.Form` class for changing :attr:`_data`."""

    _default_data = {}
    """The default data dictionary to create from the start.

    If you plan to store something in :attr:`_data`, declare it in
    this dict for documentation purposes, if nothing else. Down the
    road, we may validate data against this dict to ensure that only
    known keys are used.
    """

    def __init__(self, data=None):
        """Initialize with the given data, or the class defaults.

        :type data: dict
        :param data: The unique parameters of this engine instance.

        """
        self._data = data or self._default_data

    def engine_params(self):
        """Return the unique parameters of this engine instance.

        :rtype: dict
        :returns: All the data necessary to create a functionally
            equivalent instance of this engine.

        """
        return self._data

    @property
    @memoize
    def settings_form(self):
        """Return an instance of :attr:`settings_form_class` if defined.

        :rtype: :class:`mediacore.forms.Form` or None
        :returns: A memoized form instance, since instantiation is expensive.

        """
        if self.settings_form_class is None:
            return None
        return self.settings_form_class()

    @abstractmethod
    def parse(self, file=None, url=None):
        """Return metadata for the given file or URL, or raise an error.

        It is expected that different storage engines will be able to
        extract different metadata.

        **Required metadata keys**:

            * type (generally 'audio' or 'video')

        **Optional metadata keys**:

            * unique_id
            * container
            * display_name
            * title
            * size
            * width
            * height
            * bitrate
            * thumbnail_file
            * thumbnail_url

        :type file: :class:`cgi.FieldStorage` or None
        :param file: A freshly uploaded file object.
        :type url: unicode or None
        :param url: A remote URL string.
        :rtype: dict
        :returns: Any extracted metadata.
        :raises UnsuitableEngineError: If file information cannot be parsed.

        """

    def store(self, media_file, file=None, url=None, meta=None):
        """Store the given file or URL and return a unique identifier for it.

        This method is called with a newly persisted instance of
        :class:`~mediacore.model.media.MediaFile`. The instance has
        been flushed and therefore has its primary key, but it has
        not yet been committed. An exception here will trigger a rollback.

        This method need not necessarily return anything. If :meth:`parse`
        returned a `unique_id` key, this can return None. It is only when
        this method generates the unique ID, or if it must override the
        unique ID from :meth:`parse`, that it should be returned here.

        This method SHOULD NOT modify the `media_file`. It is provided
        for informational purposes only, so that a unique ID may be
        generated with the primary key from the database.

        :type media_file: :class:`~mediacore.model.media.MediaFile`
        :param media_file: The associated media file object.
        :type file: :class:`cgi.FieldStorage` or None
        :param file: A freshly uploaded file object.
        :type url: unicode or None
        :param url: A remote URL string.
        :type meta: dict
        :param meta: The metadata returned by :meth:`parse`.
        :rtype: unicode or None
        :returns: The unique ID string. Return None if not generating it here.

        """

    def delete(self, unique_id):
        """Delete the stored file represented by the given unique ID.

        :type unique_id: unicode
        :param unique_id: The identifying string for this file.
        :rtype: boolean
        :returns: True if successful, False if an error occurred.

        """

    @abstractmethod
    def get_uris(self, file):
        """Return a list of URIs from which the stored file can be accessed.

        :type media_file: :class:`~mediacore.model.media.MediaFile`
        :param media_file: The associated media file object.
        :rtype: list
        :returns: All :class:`StorageURI` tuples for this file.

        """

class FileStorageEngine(StorageEngine):
    """
    Helper subclass that parses file uploads for basic metadata.
    """

    is_singleton = False

    def parse(self, file=None, url=None):
        """Return metadata for the given file or raise an error.

        :type file: :class:`cgi.FieldStorage` or None
        :param file: A freshly uploaded file object.
        :type url: unicode or None
        :param url: A remote URL string.
        :rtype: dict
        :returns: Any extracted metadata.
        :raises UnsuitableEngineError: If file information cannot be parsed.

        """
        if file is None:
            raise UnsuitableEngineError

        filename = os.path.basename(file.filename)
        name, ext = os.path.splitext(filename)
        ext = ext.lstrip('.').lower()
        container = guess_container_format(ext)

        return {
            'type': guess_media_type(container),
            'container': container,
            'display_name': u'%s.%s' % (name, container or ext),
            'size': get_file_size(file.file),
        }

class EmbedStorageEngine(StorageEngine):
    """
    A specialized URL storage engine for URLs that match a certain pattern.
    """

    is_singleton = True

    url_pattern = abstractproperty()
    """A compiled pattern object that uses named groupings for matches."""

    def parse(self, file=None, url=None):
        """Return metadata for the given URL or raise an error.

        If the given URL matches :attr:`url_pattern` then :meth:`_parse`
        is called with the named matches as kwargs and the result returned.

        :type file: :class:`cgi.FieldStorage` or None
        :param file: A freshly uploaded file object.
        :type url: unicode or None
        :param url: A remote URL string.
        :rtype: dict
        :returns: Any extracted metadata.
        :raises UnsuitableEngineError: If file information cannot be parsed.

        """
        if url is None:
            raise UnsuitableEngineError
        match = self.url_pattern.match(url)
        if match is None:
            raise UnsuitableEngineError
        return self._parse(url, **match.groupdict())

    @abstractmethod
    def _parse(self, url, **kwargs):
        """Return metadata for the given URL that matches :attr:`url_pattern`.

        :type url: unicode
        :param url: A remote URL string.
        :param \*\*kwargs: The named matches from the url match object.
        :rtype: dict
        :returns: Any extracted metadata.

        """

def add_new_media_file(media, file=None, url=None):
    """Create a MediaFile instance from the given file or URL.

    This function MAY modify the given media object.

    :type media: :class:`~mediacore.model.media.Media` instance
    :param media: The media object that this file or URL will belong to.
    :type file: :class:`cgi.FieldStorage` or None
    :param file: A freshly uploaded file object.
    :type url: unicode or None
    :param url: A remote URL string.
    :rtype: :class:`~mediacore.model.media.MediaFile`
    :returns: A newly created media file instance.
    :raises formencode.Invalid: If the input file or URL cannot be
        stored with any of the registered storage engines.

    """
    from mediacore.model import DBSession, MediaFile
    from mediacore.model.storage import fetch_engines

    for engine in fetch_engines():
        try:
            meta = engine.parse(file=file, url=url)
            log.debug('Engine %r returned meta %r', engine, meta)
            break
        except UnsuitableEngineError:
            log.debug('Engine %r unsuitable for %r/%r', engine, file, url)
            continue
    else:
        raise Invalid(_('Unusable file or URL provided.'), None, None)

    mf = MediaFile()
    mf.storage = engine
    mf.media = media

    mf.type = meta['type']
    mf.display_name = meta.get('display_name', default_display_name(file, url))
    mf.unique_id = meta.get('unique_id', None)

    mf.container = meta.get('container', None)
    mf.size = meta.get('size', None)
    mf.bitrate = meta.get('bitrate', None)
    mf.width = meta.get('width', None)
    mf.height = meta.get('height', None)

    media.files.append(mf)
    DBSession.flush()

    unique_id = engine.store(media_file=mf, file=file, url=url, meta=meta)

    if unique_id:
        mf.unique_id = unique_id
    elif not mf.unique_id:
        raise StorageError('Engine %r returned no unique ID.', engine)

    if not media.duration and meta.get('duration', 0):
        media.duration = meta['duration']
    if not media.title:
        media.title = meta.get('title', None) or mf.display_name

    if ('thumbnail_url' in meta or 'thumbnail_file' in meta) \
    and (not has_thumbs(media) or has_default_thumbs(media)):
        thumb_file = meta.get('thumbnail_file', None)

        if thumb_file is not None:
            thumb_filename = thumb_file.filename
        else:
            thumb_url = meta['thumbnail_url']
            thumb_filename = os.path.basename(thumb_url)

            # Download the image to a buffer and wrap it as a file-like object
            try:
                temp_img = urlopen(thumb_url)
                thumb_file = StringIO(temp_img.read())
                temp_img.close()
            except URLError, e:
                log.exception(e)

        if thumb_file is not None:
            create_thumbs_for(media, thumb_file, thumb_filename)
            thumb_file.close()

    DBSession.flush()

    return mf

def get_file_size(file):
    if hasattr(file, 'fileno'):
        size = os.fstat(file.fileno())[6]
    else:
        file.seek(0, os.SEEK_END)
        size = file.tell()
        file.seek(0)
    return size

def default_display_name(file=None, url=None):
    if file is not None:
        return file.filename
    return os.path.basename(url or '')

def default_file_name(media_file):
    media = media_file.media
    file_name = '%d_%d_%s.%s' % (media.id, media_file.id, media.slug,
                                 media_file.container)
    return file_name

from mediacore.lib.storage.localfiles import LocalFileStorage
from mediacore.lib.storage.ftp import FTPStorage
from mediacore.lib.storage.s3 import AmazonS3Storage
from mediacore.lib.storage.youtube import YoutubeStorage
from mediacore.lib.storage.vimeo import VimeoStorage
from mediacore.lib.storage.bliptv import BlipTVStorage
from mediacore.lib.storage.googlevideo import GoogleVideoStorage
from mediacore.lib.storage.remoteurls import RemoteURLStorage
