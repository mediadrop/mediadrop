# This file is a part of MediaDrop (http://www.mediadrop.net),
# Copyright 2009-2013 MediaDrop contributors
# For the exact contribution history, see the git revision log.
# The source code contained in this file is licensed under the GPLv3 or
# (at your option) any later version.
# See LICENSE.txt in the main project directory, for more information.

import os

from urlparse import urlsplit

from mediacore.lib.compat import all

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

def pick_uris(uris, **kwargs):
    """Return a subset of the given URIs whose attributes match the kwargs.

    This function attempts to simplify the somewhat unwieldly process of
    filtering a list of :class:`mediacore.lib.storage.StorageURI` instances
    for a specific type, protocol, container, etc::

        pick_uris(uris, scheme='rtmp', container='mp4', type='video')

    :type uris: iterable or :class:`~mediacore.model.media.Media` or
        :class:`~mediacore.model.media.MediaFile` instance
    :params uris: A collection of :class:`~mediacore.lib.storage.StorageURI`
        instances, including Media and MediaFile objects.
    :param \*\*kwargs: Required attribute values. These attributes can be
        on the `StorageURI` instance or, failing that, on the `StorageURI.file`
        instance within it.
    :rtype: list
    :returns: A subset of the input `uris`.

    """
    if not isinstance(uris, (list, tuple)):
        from mediacore.model.media import Media, MediaFile
        if isinstance(uris, (Media, MediaFile)):
            uris = uris.get_uris()
    if not uris or not kwargs:
        return uris
    return [uri
            for uri in uris
            if all(getattr(uri, k) == v for k, v in kwargs.iteritems())]

def pick_uri(uris, **kwargs):
    """Return the first URL that meets the given criteria.

    See: :func:`pick_uris`.

    :returns: A :class:`mediacore.lib.storage.StorageURI` instance or None.
    """
    uris = pick_uris(uris, **kwargs)
    if uris:
        return uris[0]
    return None

def download_uri(uris):
    """Pick out the best possible URI for downloading purposes.

    :returns: A :class:`mediacore.lib.storage.StorageURI` instance or None.
    """
    uris = pick_uris(uris, scheme='download')\
        or pick_uris(uris, scheme='http')
    uris.sort(key=lambda uri: uri.file.size, reverse=True)
    if uris:
        return uris[0]
    return None

def web_uri(uris):
    """Pick out the web link URI for viewing an embed in its original context.

    :returns: A :class:`mediacore.lib.storage.StorageURI` instance or None.
    """
    return pick_uri(uris, scheme='www')\
        or None

def best_link_uri(uris):
    """Pick out the best general purpose URI from those given.

    :returns: A :class:`mediacore.lib.storage.StorageURI` instance or None.
    """
    return pick_uri(uris, scheme='www')\
        or pick_uri(uris, scheme='download')\
        or pick_uri(uris, scheme='http')\
        or pick_uri(uris)\
        or None

def file_path(uris):
    """Pick out the local file path from the given list of URIs.

    Local file paths are passed around as urlencoded strings in
    :class:`mediacore.lib.storage.StorageURI`. The form is:

        file:///path/to/file

    :rtype: `str` or `unicode` or `None`
    :returns: Absolute /path/to/file
    """
    uris = pick_uris(uris, scheme='file')
    if uris:
        scheme, netloc, path, query, fragment = urlsplit(uris[0].file_uri)
        return path
    return None
