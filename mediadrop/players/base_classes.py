# -*- coding: utf-8 -*-
# This file is a part of MediaDrop (https://www.mediadrop.video),
# Copyright 2009-2018 MediaDrop contributors
# For the exact contribution history, see the git revision log.
# The source code contained in this file is licensed under the GPLv3 or
# (at your option) any later version.
# See LICENSE.txt in the main project directory, for more information.

from datetime import datetime
from urllib import urlencode

from genshi.builder import Element
from genshi.core import Markup
import simplejson
from sqlalchemy import sql

from mediadrop.lib.filetypes import AUDIO, VIDEO
from mediadrop.lib.thumbnails import thumb_url
from mediadrop.lib.uri import pick_uris
from mediadrop.plugin.abc import AbstractClass, abstractmethod, abstractproperty


__all__ = [
    'AbstractFlashPlayer',
    'AbstractHTML5Player',
    'AbstractPlayer',
    'AbstractRTMPFlashPlayer',
    'FileSupportMixin',
    'HTTP',
    'RTMP'
]

HTTP, RTMP = 'http', 'rtmp'

###############################################################################

class AbstractPlayer(AbstractClass):
    """
    Player Base Class that all players must implement.
    """

    name = abstractproperty()
    """A unicode string identifier for this class."""

    display_name = abstractproperty()
    """A unicode display name for the class, to be used in the settings UI."""

    settings_form_class = None
    """An optional :class:`mediadrop.forms.admin.players.PlayerPrefsForm`."""

    default_data = {}
    """An optional default data dictionary for user preferences."""

    supports_resizing = True
    """A flag that allows us to mark the few players that can't be resized.

    Setting this to False ensures that the resize (expand/shrink) controls will
    not be shown in our player control bar.
    """

    @abstractmethod
    def can_play(self, uris):
        """Test all the given URIs to see if they can be played by this player.

        This is a class method, not an instance or static method.

        :type uris: list
        :param uris: A collection of StorageURI tuples to test.
        :rtype: tuple
        :returns: Boolean result for each of the given URIs.

        """

    def render_markup(self, error_text=None):
        """Render the XHTML markup for this player instance.

        :param error_text: Optional error text that should be included in
            the final markup if appropriate for the player.
        :rtype: ``unicode`` or :class:`genshi.core.Markup`
        :returns: XHTML that will not be escaped by Genshi.

        """
        return error_text or u''

    @abstractmethod
    def render_js_player(self):
        """Render a javascript string to instantiate a javascript player.

        Each player has a client-side component to provide a consistent
        way of initializing and interacting with the player. For more
        information see :file:`mediadrop/public/scripts/mcore/players/`.

        :rtype: ``unicode``
        :returns: A javascript string which will evaluate to an instance
            of a JS player class. For example: ``new mcore.Html5Player()``.

        """

    def __init__(self, media, uris, data=None, width=None, height=None,
                 autoplay=False, autobuffer=False, qualified=False, **kwargs):
        """Initialize the player with the media that it will be playing.

        :type media: :class:`mediadrop.model.media.Media` instance
        :param media: The media object that will be rendered.
        :type uris: list
        :param uris: The StorageURIs this player has said it :meth:`can_play`.
        :type data: dict or None
        :param data: Optional player preferences from the database.
        :type elem_id: unicode, None, Default
        :param elem_id: The element ID to use when rendering. If left
            undefined, a sane default value is provided. Use None to disable.

        """
        self.media = media
        self.uris = uris
        self.data = data or {}
        self.width = width or 400
        self.height = height or 225
        self.autoplay = autoplay
        self.autobuffer = autobuffer
        self.qualified = qualified
        self.elem_id = kwargs.pop('elem_id', '%s-player' % media.slug)

    _width_diff = 0
    _height_diff = 0

    @property
    def adjusted_width(self):
        """Return the desired viewable width + any extra for the player."""
        return self.width + self._width_diff

    @property
    def adjusted_height(self):
        """Return the desired viewable height + the height of the controls."""
        return self.height + self._height_diff

    def get_uris(self, **kwargs):
        """Return a subset of the :attr:`uris` for this player.

        This allows for easy filtering of URIs by feeding any number of
        kwargs to this function. See :func:`mediadrop.lib.uri.pick_uris`.

        """
        return pick_uris(self.uris, **kwargs)
    
    @classmethod
    def inject_in_db(cls, enable_player=False):
        from mediadrop.model import DBSession
        from mediadrop.model.players import players as players_table, PlayerPrefs
        
        prefs = PlayerPrefs()
        prefs.name = cls.name
        prefs.enabled = enable_player
        
        # MySQL does not allow referencing the same table in a subquery
        # (i.e. insert, max): http://stackoverflow.com/a/14302701/138526
        # Therefore we need to alias the table in max
        current_max_query = sql.select([sql.func.max(players_table.alias().c.priority)])
        # sql.func.coalesce == "set default value if func.max does "
        # In case there are no players in the database the current max is NULL. With
        # coalesce we can set a default value.
        new_priority_query = sql.func.coalesce(
            current_max_query.as_scalar()+1,
            1
        )
        prefs.priority = new_priority_query
        
        prefs.created_on = datetime.now()
        prefs.modified_on = datetime.now()
        prefs.data = cls.default_data
        DBSession.add(prefs)
        DBSession.commit()



###############################################################################

class FileSupportMixin(object):
    """
    Mixin that provides a can_play test on a number of common parameters.
    """
    supported_containers = abstractproperty()
    supported_schemes = set([HTTP])
    supported_types = set([AUDIO, VIDEO])

    @classmethod
    def can_play(cls, uris):
        """Test all the given URIs to see if they can be played by this player.

        This is a class method, not an instance or static method.

        :type uris: list
        :param uris: A collection of StorageURI tuples to test.
        :rtype: tuple
        :returns: Boolean result for each of the given URIs.

        """
        playable = []
        for uri in uris:
            is_type_ok = (uri.file.type in cls.supported_types)
            is_scheme_ok = (uri.scheme in cls.supported_schemes)
            is_container_ok = (not uri.file.container) or (uri.file.container in cls.supported_containers)
            is_playable = is_type_ok and is_scheme_ok and is_container_ok
            playable.append(is_playable)
        return tuple(playable)

class FlashRenderMixin(object):
    """
    Mixin for rendering flash players. Used by embedtypes as well as flash.
    """

    def render_object_embed(self, error_text=None):
        object_tag = self.render_object()
        orig_id = self.elem_id
        self.elem_id = None
        embed_tag = self.render_embed(error_text)
        self.elem_id = orig_id
        return object_tag(embed_tag)

    def render_embed(self, error_text=None):
        swf_url = self.swf_url()
        flashvars = urlencode(self.flashvars())

        tag = Element('embed', type='application/x-shockwave-flash',
                      allowfullscreen='true', allowscriptaccess='always',
                      width=self.adjusted_width, height=self.adjusted_height,
                      src=swf_url, flashvars=flashvars, id=self.elem_id)
        if error_text:
            tag(error_text)
        return tag

    def render_object(self, error_text=None):
        swf_url = self.swf_url()
        flashvars = urlencode(self.flashvars())

        tag = Element('object', type='application/x-shockwave-flash',
                      width=self.adjusted_width, height=self.adjusted_height,
                      data=swf_url, id=self.elem_id)
        tag(Element('param', name='movie', value=swf_url))
        tag(Element('param', name='flashvars', value=flashvars))
        tag(Element('param', name='allowfullscreen', value='true'))
        tag(Element('param', name='allowscriptaccess', value='always'))
        if error_text:
            tag(error_text)
        return tag

    def render_js_player(self):
        """Render a javascript string to instantiate a javascript player.

        Each player has a client-side component to provide a consistent
        way of initializing and interacting with the player. For more
        information see ``mediadrop/public/scripts/mcore/players/``.

        :rtype: ``unicode``
        :returns: A javascript string which will evaluate to an instance
            of a JS player class. For example: ``new mcore.Html5Player()``.

        """
        return Markup("new mcore.FlashPlayer('%s', %d, %d, %s)" % (
            self.swf_url(),
            self.adjusted_width,
            self.adjusted_height,
            simplejson.dumps(self.flashvars()),
        ))

###############################################################################

class AbstractFlashPlayer(FileSupportMixin, FlashRenderMixin, AbstractPlayer):
    """
    Base Class for standard Flash Players.

    This does not typically include flash players from other vendors
    such as embed types.

    """
    supported_containers = set(['mp3', 'mp4', 'flv', 'f4v', 'flac'])

    @abstractmethod
    def flashvars(self):
        """Return a python dict of flashvars for this player."""

    @abstractmethod
    def swf_url(self):
        """Return the flash player URL."""

class AbstractRTMPFlashPlayer(AbstractFlashPlayer):
    """
    Dummy Base Class for Flash Players that can stream over RTMP.

    """
    supported_schemes = set([HTTP, RTMP])

###############################################################################

class AbstractEmbedPlayer(AbstractPlayer):
    """
    Abstract Embed Player for third-party services like YouTube

    Typically embed players will play only their own content, and that is
    the only way such content can be played. Therefore each embed type has
    been given its own :attr:`~mediadrop.lib.uri.StorageURI.scheme` which
    uniquely identifies it.

    For example, :meth:`mediadrop.lib.storage.YoutubeStorage.get_uris`
    returns URIs with a scheme of `'youtube'`, and the special
    :class:`YoutubePlayer` would overload :attr:`scheme` to also be
    `'youtube'`. This would allow the Youtube player to play only those URIs.

    """
    scheme = abstractproperty()
    """The `StorageURI.scheme` which uniquely identifies this embed type."""

    @classmethod
    def can_play(cls, uris):
        """Test all the given URIs to see if they can be played by this player.

        This is a class method, not an instance or static method.

        :type uris: list
        :param uris: A collection of StorageURI tuples to test.
        :rtype: tuple
        :returns: Boolean result for each of the given URIs.

        """
        return tuple(uri.scheme == cls.scheme for uri in uris)

class AbstractIframeEmbedPlayer(AbstractEmbedPlayer):
    """
    Abstract Embed Player for services that provide an iframe player.

    """
    def render_js_player(self):
        """Render a javascript string to instantiate a javascript player.

        Each player has a client-side component to provide a consistent
        way of initializing and interacting with the player. For more
        information see ``mediadrop/public/scripts/mcore/players/``.

        :rtype: ``unicode``
        :returns: A javascript string which will evaluate to an instance
            of a JS player class. For example: ``new mcore.Html5Player()``.

        """
        return Markup("new mcore.IframePlayer()")

class AbstractFlashEmbedPlayer(FlashRenderMixin, AbstractEmbedPlayer):
    """
    Simple Abstract Flash Embed Player

    Provides sane defaults for most flash-based embed players from
    third-party vendors, which typically never need any flashvars
    or special configuration.

    """
    def swf_url(self):
        """Return the flash player URL."""
        return str(self.uris[0])

    def flashvars(self):
        """Return a python dict of flashvars for this player."""
        return {}


class AbstractHTML5Player(FileSupportMixin, AbstractPlayer):
    """
    HTML5 <audio> / <video> tag.

    References:

        - http://dev.w3.org/html5/spec/Overview.html#audio
        - http://dev.w3.org/html5/spec/Overview.html#video
        - http://developer.apple.com/safari/library/documentation/AudioVideo/Conceptual/Using_HTML5_Audio_Video/Introduction/Introduction.html

    """
    supported_containers = set(['mp3', 'mp4', 'ogg', 'webm', 'm3u8'])
    supported_schemes = set([HTTP])

    def __init__(self, *args, **kwargs):
        super(AbstractHTML5Player, self).__init__(*args, **kwargs)
        # Move mp4 files to the front of the list because the iPad has
        # a bug that prevents it from playing but the first file.
        self.uris.sort(key=lambda uri: uri.file.container != 'mp4')
        self.uris.sort(key=lambda uri: uri.file.container != 'm3u8')

    def html5_attrs(self):
        attrs = {
            'id': self.elem_id,
            'controls': 'controls',
            'width': self.adjusted_width,
            'height': self.adjusted_height,
        }
        if self.autoplay:
            attrs['autoplay'] = 'autoplay'
        elif self.autobuffer:
            # This isn't included in the HTML5 spec, but Safari supports it
            attrs['autobuffer'] = 'autobuffer'
        if self.media.type == VIDEO:
            attrs['poster'] = thumb_url(self.media, 'l',
                                        qualified=self.qualified)
        return attrs

    def render_markup(self, error_text=None):
        """Render the XHTML markup for this player instance.

        :param error_text: Optional error text that should be included in
            the final markup if appropriate for the player.
        :rtype: ``unicode`` or :class:`genshi.core.Markup`
        :returns: XHTML that will not be escaped by Genshi.

        """
        attrs = self.html5_attrs()
        tag = Element(self.media.type, **attrs)
        for uri in self.uris:
            # Providing a type attr breaks for m3u8 breaks iPhone playback.
            # Tried: application/x-mpegURL, vnd.apple.mpegURL, video/MP2T
            if uri.file.container == 'm3u8':
                mimetype = None
            else:
                mimetype = uri.file.mimetype
            tag(Element('source', src=uri, type=mimetype))
        if error_text:
            tag(error_text)
        return tag

    def render_js_player(self):
        return Markup("new mcore.Html5Player()")
