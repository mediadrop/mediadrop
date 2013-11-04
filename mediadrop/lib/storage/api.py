# This file is a part of MediaDrop (http://www.mediadrop.net),
# Copyright 2009-2013 MediaDrop contributors
# For the exact contribution history, see the git revision log.
# The source code contained in this file is licensed under the GPLv3 or
# (at your option) any later version.
# See LICENSE.txt in the main project directory, for more information.

import logging
import os
import re

from cStringIO import StringIO
from operator import attrgetter
from urllib2 import URLError, urlopen

from mediadrop.lib.compat import defaultdict, SEEK_END
from mediadrop.lib.decorators import memoize
from mediadrop.lib.filetypes import guess_container_format, guess_media_type
from mediadrop.lib.i18n import _
from mediadrop.lib.thumbnails import (create_thumbs_for, has_thumbs,
    has_default_thumbs)
from mediadrop.lib.xhtml import clean_xhtml
from mediadrop.plugin.abc import (AbstractClass, abstractmethod,
    abstractproperty)

__all__ = ['add_new_media_file', 'sort_engines', 'CannotTranscode', 
    'FileStorageEngine', 'StorageError', 'StorageEngine', 
    'UnsuitableEngineError', 'UserStorageError',
]

log = logging.getLogger(__name__)


class StorageError(Exception):
    """Base class for all storage exceptions."""

class UserStorageError(StorageError):
    """A storage error that occurs due to the user input.

    The message will be displayed to the user."""

class UnsuitableEngineError(StorageError):
    """Error to indicate that StorageEngine.parse can't parse its input."""

class CannotTranscode(StorageError):
    """Exception to indicate that StorageEngine.transcode can't or won't transcode a given file."""

class StorageEngine(AbstractClass):
    """
    Base class for all Storage Engine implementations.
    """

    engine_type = abstractproperty()
    """A unique identifying unicode string for the StorageEngine."""

    default_name = abstractproperty()
    """A user-friendly display name that identifies this StorageEngine."""

    is_singleton = abstractproperty()
    """A flag that indicates whether this engine should be added only once."""

    settings_form_class = None
    """Your :class:`mediadrop.forms.Form` class for changing :attr:`_data`."""

    _default_data = {}
    """The default data dictionary to create from the start.

    If you plan to store something in :attr:`_data`, declare it in
    this dict for documentation purposes, if nothing else. Down the
    road, we may validate data against this dict to ensure that only
    known keys are used.
    """

    try_before = []
    """Storage Engines that should :meth:`parse` after this class has.

    This is a list of StorageEngine class objects which is used to
    perform a topological sort of engines. See :func:`sort_engines`
    and :func:`add_new_media_file`.
    """

    try_after = []
    """Storage Engines that should :meth:`parse` before this class has.

    This is a list of StorageEngine class objects which is used to
    perform a topological sort of engines. See :func:`sort_engines`
    and :func:`add_new_media_file`.
    """

    def __init__(self, display_name=None, data=None):
        """Initialize with the given data, or the class defaults.

        :type display_name: unicode
        :param display_name: Name, defaults to :attr:`default_name`.
        :type data: dict
        :param data: The unique parameters of this engine instance.

        """
        self.display_name = display_name or self.default_name
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

        :rtype: :class:`mediadrop.forms.Form` or None
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
        :class:`~mediadrop.model.media.MediaFile`. The instance has
        been flushed and therefore has its primary key, but it has
        not yet been committed. An exception here will trigger a rollback.

        This method need not necessarily return anything. If :meth:`parse`
        returned a `unique_id` key, this can return None. It is only when
        this method generates the unique ID, or if it must override the
        unique ID from :meth:`parse`, that it should be returned here.

        This method SHOULD NOT modify the `media_file`. It is provided
        for informational purposes only, so that a unique ID may be
        generated with the primary key from the database.

        :type media_file: :class:`~mediadrop.model.media.MediaFile`
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

    def postprocess(self, media_file):
        """Perform additional post-processing after the save is complete.

        This is called after :meth:`parse`, :meth:`store`, thumbnails
        have been saved and the changes to database flushed.

        :type media_file: :class:`~mediadrop.model.media.MediaFile`
        :param media_file: The associated media file object.
        :returns: None

        """

    def delete(self, unique_id):
        """Delete the stored file represented by the given unique ID.

        :type unique_id: unicode
        :param unique_id: The identifying string for this file.
        :rtype: boolean
        :returns: True if successful, False if an error occurred.

        """

    def transcode(self, media_file):
        """Transcode an existing MediaFile.

        The MediaFile may be stored already by another storage engine.
        New MediaFiles will be created for each transcoding generated by this
        method.

        :type media_file: :class:`~mediadrop.model.media.MediaFile`
        :param media_file: The MediaFile object to transcode.
        :raises CannotTranscode: If this storage engine can't or won't transcode the file.
        :rtype: NoneType
        :returns: Nothing

        """
        raise CannotTranscode('This StorageEngine does not support transcoding.')

    @abstractmethod
    def get_uris(self, media_file):
        """Return a list of URIs from which the stored file can be accessed.

        :type media_file: :class:`~mediadrop.model.media.MediaFile`
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

    try_after = [FileStorageEngine]

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

def enabled_engines():
    from mediadrop.model import DBSession
    engines = DBSession.query(StorageEngine)\
        .filter(StorageEngine.enabled == True)\
        .all()
    return list(sort_engines(engines))

def add_new_media_file(media, file=None, url=None):
    """Create a MediaFile instance from the given file or URL.

    This function MAY modify the given media object.

    :type media: :class:`~mediadrop.model.media.Media` instance
    :param media: The media object that this file or URL will belong to.
    :type file: :class:`cgi.FieldStorage` or None
    :param file: A freshly uploaded file object.
    :type url: unicode or None
    :param url: A remote URL string.
    :rtype: :class:`~mediadrop.model.media.MediaFile`
    :returns: A newly created media file instance.
    :raises StorageError: If the input file or URL cannot be
        stored with any of the registered storage engines.

    """
    sorted_engines = enabled_engines()
    for engine in sorted_engines:
        try:
            meta = engine.parse(file=file, url=url)
            log.debug('Engine %r returned meta %r', engine, meta)
            break
        except UnsuitableEngineError:
            log.debug('Engine %r unsuitable for %r/%r', engine, file, url)
            continue
    else:
        raise StorageError(_('Unusable file or URL provided.'), None, None)

    from mediadrop.model import DBSession, MediaFile
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
    if not media.description and meta.get('description'):
        media.description = clean_xhtml(meta['description'])
    if not media.title:
        media.title = meta.get('title', None) or mf.display_name
    if media.type is None:
        media.type = mf.type

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

    engine.postprocess(mf)

    # Try to transcode the file.
    for engine in sorted_engines:
        try:
            engine.transcode(mf)
            log.debug('Engine %r has agreed to transcode %r', engine, mf)
            break
        except CannotTranscode:
            log.debug('Engine %r unsuitable for transcoding %r', engine, mf)
            continue

    return mf

def sort_engines(engines):
    """Yield a topological sort of the given list of engines.

    :type engines: list
    :param engines: Unsorted instances of :class:`StorageEngine`.

    """
    # Partial ordering of engine classes, keys come before values.
    edges = defaultdict(set)

    # Collection of engine instances grouped by their class.
    engine_objs = defaultdict(set)

    # Find all edges between registered engine classes
    for engine in engines:
        engine_cls = engine.__class__
        engine_objs[engine_cls].add(engine)
        for edge_cls in engine.try_before:
            edges[edge_cls].add(engine_cls)
            for edge_cls_implementation in edge_cls:
                edges[edge_cls_implementation].add(engine_cls)
        for edge_cls in engine.try_after:
            edges[engine_cls].add(edge_cls)
            for edge_cls_implementation in edge_cls:
                edges[engine_cls].add(edge_cls_implementation)

    # Iterate over the engine classes
    todo = set(engine_objs.iterkeys())
    while todo:
        # Pull out classes that have no unsatisfied edges
        output = set()
        for engine_cls in todo:
            if not todo.intersection(edges[engine_cls]):
                output.add(engine_cls)
        if not output:
            raise RuntimeError('Circular dependency detected.')
        todo.difference_update(output)

        # Collect all the engine instances we'll be returning in this round,
        # ordering them by ID to give consistent results each time we run this.
        output_instances = []
        for engine_cls in output:
            output_instances.extend(engine_objs[engine_cls])
        output_instances.sort(key=attrgetter('id'))

        for engine in output_instances:
            yield engine

def get_file_size(file):
    if hasattr(file, 'fileno'):
        size = os.fstat(file.fileno())[6]
    else:
        file.seek(0, SEEK_END)
        size = file.tell()
        file.seek(0)
    return size

def default_display_name(file=None, url=None):
    if file is not None:
        return file.filename
    return os.path.basename(url or '')

_filename_filter = re.compile(r'[^a-z0-9_-]')

def safe_file_name(media_file, hint=None):
    """Return a safe filename for the given MediaFile.

    The base path, extension and non-alphanumeric characters are
    stripped from the filename hint so all that remains is what the
    user named the file, to give some idea of what the file contains
    when viewing the filesystem.

    :param media_file: A :class:`~mediadrop.model.media.MediaFile`
        instance that has been flushed to the database.
    :param hint: Optionally the filename provided by the user.
    :returns: A filename with the MediaFile.id, a filtered hint
        and the MediaFile.container.

    """
    if not isinstance(hint, basestring):
        hint = u''
    # Prevent malicious paths like /etc/passwd
    hint = os.path.basename(hint)
    # IE provides full file paths instead of names C:\path\to\file.mp4
    hint = hint.split('\\')[-1]
    hint, orig_ext = os.path.splitext(hint)
    hint = hint.lower()
    # Remove any non-alphanumeric characters
    hint = _filename_filter.sub('', hint)
    if hint:
        hint = u'-%s' % hint
    if media_file.container:
        ext = u'.%s' % media_file.container
    else:
        ext = u''
    return u'%d%s%s' % (media_file.id, hint, ext)

