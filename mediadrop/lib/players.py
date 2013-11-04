# This file is a part of MediaDrop (http://www.mediadrop.net),
# Copyright 2009-2013 MediaDrop contributors
# For the exact contribution history, see the git revision log.
# The source code contained in this file is licensed under the GPLv3 or
# (at your option) any later version.
# See LICENSE.txt in the main project directory, for more information.

from datetime import datetime
from itertools import izip
import logging
from urllib import urlencode

from genshi.builder import Element
from genshi.core import Markup
import simplejson
from sqlalchemy import sql

from mediadrop.forms.admin import players as player_forms
from mediadrop.lib.compat import any
from mediadrop.lib.filetypes import AUDIO, VIDEO, AUDIO_DESC, CAPTIONS
from mediadrop.lib.i18n import N_
from mediadrop.lib.templating import render
from mediadrop.lib.thumbnails import thumb_url
from mediadrop.lib.uri import pick_uris
from mediadrop.lib.util import url_for
#from mediadrop.model.players import fetch_players XXX: Import at EOF
from mediadrop.plugin.abc import AbstractClass, abstractmethod, abstractproperty

log = logging.getLogger(__name__)

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
    def can_play(cls, uris):
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
        # didn't get direct SQL expression to work with SQLAlchemy
        # player_table = sql.func.max(player_table.c.priority)
        query = sql.select([sql.func.max(players_table.c.priority)])
        max_priority = DBSession.execute(query).first()[0]
        if max_priority is None:
            max_priority = -1
        prefs.priority = max_priority + 1
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
        return tuple(uri.file.container in cls.supported_containers
                     and uri.scheme in cls.supported_schemes
                     and uri.file.type in cls.supported_types
                     for uri in uris)

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

class FlowPlayer(AbstractFlashPlayer):
    """
    FlowPlayer (Flash)
    """
    name = u'flowplayer'
    """A unicode string identifier for this class."""

    display_name = N_(u'Flowplayer')
    """A unicode display name for the class, to be used in the settings UI."""

    supported_schemes = set([HTTP])

    def swf_url(self):
        """Return the flash player URL."""
        return url_for('/scripts/third-party/flowplayer/flowplayer-3.2.14.swf',
                       qualified=self.qualified)

    def flashvars(self):
        """Return a python dict of flashvars for this player."""
        http_uri = self.uris[0]

        playlist = []
        vars = {
            'canvas': {'backgroundColor': '#000', 'backgroundGradient': 'none'},
            'plugins': {
                'controls': {'autoHide': True},
            },
            'clip': {'scaling': 'fit'},
            'playlist': playlist,
        }

        # Show a preview image
        if self.media.type == AUDIO or not self.autoplay:
            playlist.append({
                'url': thumb_url(self.media, 'l', qualified=self.qualified),
                'autoPlay': True,
                'autoBuffer': True,
            })

        playlist.append({
            'url': str(http_uri),
            'autoPlay': self.autoplay,
            'autoBuffer': self.autoplay or self.autobuffer,
        })

        # Flowplayer wants these options passed as an escaped JSON string
        # inside a single 'config' flashvar. When using the flowplayer's
        # own JS, this is automatically done, but since we use Swiff, a
        # SWFObject clone, we have to do this ourselves.
        vars = {'config': simplejson.dumps(vars, separators=(',', ':'))}
        return vars

AbstractFlashPlayer.register(FlowPlayer)

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


class VimeoUniversalEmbedPlayer(AbstractIframeEmbedPlayer):
    """
    Vimeo Universal Player

    This simple player handles media with files that stored using
    :class:`mediadrop.lib.storage.VimeoStorage`.

    This player has seamless HTML5 and Flash support.

    """
    name = u'vimeo'
    """A unicode string identifier for this class."""

    display_name = N_(u'Vimeo')
    """A unicode display name for the class, to be used in the settings UI."""

    scheme = u'vimeo'
    """The `StorageURI.scheme` which uniquely identifies this embed type."""

    def render_markup(self, error_text=None):
        """Render the XHTML markup for this player instance.

        :param error_text: Optional error text that should be included in
            the final markup if appropriate for the player.
        :rtype: ``unicode`` or :class:`genshi.core.Markup`
        :returns: XHTML that will not be escaped by Genshi.

        """
        uri = self.uris[0]
        tag = Element('iframe', src=uri, frameborder=0,
                      width=self.adjusted_width, height=self.adjusted_height)
        return tag

AbstractIframeEmbedPlayer.register(VimeoUniversalEmbedPlayer)


class DailyMotionEmbedPlayer(AbstractIframeEmbedPlayer):
    """
    Daily Motion Universal Player

    This simple player handles media with files that stored using
    :class:`mediadrop.lib.storage.DailyMotionStorage`.

    This player has seamless HTML5 and Flash support.

    """
    name = u'dailymotion'
    """A unicode string identifier for this class."""

    display_name = N_(u'Daily Motion')
    """A unicode display name for the class, to be used in the settings UI."""

    scheme = u'dailymotion'
    """The `StorageURI.scheme` which uniquely identifies this embed type."""

    def render_markup(self, error_text=None):
        """Render the XHTML markup for this player instance.

        :param error_text: Optional error text that should be included in
            the final markup if appropriate for the player.
        :rtype: ``unicode`` or :class:`genshi.core.Markup`
        :returns: XHTML that will not be escaped by Genshi.

        """
        uri = self.uris[0]
        data = urlencode({
            'width': 560, # XXX: The native height for this width is 420
            'theme': 'none',
            'iframe': 1,
            'autoPlay': 0,
            'hideInfos': 1,
            'additionalInfos': 1,
            'foreground': '#F7FFFD',
            'highlight': '#FFC300',
            'background': '#171D1B',
        })
        tag = Element('iframe', src='%s?%s' % (uri, data), frameborder=0,
                      width=self.adjusted_width, height=self.adjusted_height)
        if error_text:
            tag(error_text)
        return tag

AbstractIframeEmbedPlayer.register(DailyMotionEmbedPlayer)


class YoutubePlayer(AbstractIframeEmbedPlayer):
    """
    YouTube Player

    This simple player handles media with files that stored using
    :class:`mediadrop.lib.storage.YoutubeStorage`.

    """
    name = u'youtube'
    """A unicode string identifier for this class."""

    display_name = N_(u'YouTube')
    """A unicode display name for the class, to be used in the settings UI."""

    scheme = u'youtube'
    """The `StorageURI.scheme` which uniquely identifies this embed type."""

    settings_form_class = player_forms.YoutubePlayerPrefsForm
    """An optional :class:`mediadrop.forms.admin.players.PlayerPrefsForm`."""

    default_data = {
        'version': 3,
        'disablekb': 0,
        'autohide': 2,
        'autoplay': 0,
        'iv_load_policy': 1,
        'modestbranding': 1,
        'fs': 1,
        'hd': 0,
        'showinfo': 0,
        'rel': 0,
        'showsearch': 0,
        'wmode': 0,
    }
    _height_diff = 25

    def render_markup(self, error_text=None):
        """Render the XHTML markup for this player instance.

        :param error_text: Optional error text that should be included in
            the final markup if appropriate for the player.
        :rtype: ``unicode`` or :class:`genshi.core.Markup`
        :returns: XHTML that will not be escaped by Genshi.

        """
        uri = self.uris[0]
        
        data = self.data.copy()
        wmode = data.pop('wmode', 0)
        if wmode:
            # 'wmode' is subject to a lot of myths and half-true statements, 
            # these are the best resources I could find:
            # http://stackoverflow.com/questions/886864/differences-between-using-wmode-transparent-opaque-or-window-for-an-embed
            # http://kb2.adobe.com/cps/127/tn_12701.html#main_Using_Window_Mode__wmode__values_
            data['wmode'] = 'opaque'
        data_qs = urlencode(data)
        iframe_attrs = dict(
            frameborder=0,
            width=self.adjusted_width,
            height=self.adjusted_height,
        )
        if bool(data.get('fs')):
            iframe_attrs.update(dict(
                allowfullscreen='',
                # non-standard attributes, required to enable YouTube's HTML5 
                # full-screen capabilities
                mozallowfullscreen='',
                webkitallowfullscreen='',
            ))
        tag = Element('iframe', src='%s?%s' % (uri, data_qs), **iframe_attrs)
        if error_text:
            tag(error_text)
        return tag


AbstractIframeEmbedPlayer.register(YoutubePlayer)


class GoogleVideoFlashPlayer(AbstractFlashEmbedPlayer):
    """
    Google Video Player

    This simple player handles media with files that stored using
    :class:`mediadrop.lib.storage.GoogleVideoStorage`.

    """
    name = u'googlevideo'
    """A unicode string identifier for this class."""

    display_name = N_(u'Google Video')
    """A unicode display name for the class, to be used in the settings UI."""

    scheme = u'googlevideo'
    """The `StorageURI.scheme` which uniquely identifies this embed type."""

    _height_diff = 27

AbstractFlashEmbedPlayer.register(GoogleVideoFlashPlayer)


class BlipTVFlashPlayer(AbstractFlashEmbedPlayer):
    """
    BlipTV Player

    This simple player handles media with files that stored using
    :class:`mediadrop.lib.storage.BlipTVStorage`.

    """
    name = u'bliptv'
    """A unicode string identifier for this class."""

    display_name = N_(u'BlipTV')
    """A unicode display name for the class, to be used in the settings UI."""

    scheme = u'bliptv'
    """The `StorageURI.scheme` which uniquely identifies this embed type."""


AbstractFlashEmbedPlayer.register(BlipTVFlashPlayer)

###############################################################################

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


class HTML5Player(AbstractHTML5Player):
    """
    HTML5 Player Implementation.

    Seperated from :class:`AbstractHTML5Player` to make it easier to subclass
    and provide a custom HTML5 player.

    """
    name = u'html5'
    """A unicode string identifier for this class."""

    display_name = N_(u'Plain HTML5 Player')
    """A unicode display name for the class, to be used in the settings UI."""

AbstractHTML5Player.register(HTML5Player)

###############################################################################

class HTML5PlusFlowPlayer(AbstractHTML5Player):
    """
    HTML5 Player with fallback to FlowPlayer.

    """
    name = u'html5+flowplayer'
    """A unicode string identifier for this class."""

    display_name = N_(u'HTML5 + Flowplayer Fallback')
    """A unicode display name for the class, to be used in the settings UI."""

    settings_form_class = player_forms.HTML5OrFlashPrefsForm
    """An optional :class:`mediadrop.forms.admin.players.PlayerPrefsForm`."""

    default_data = {'prefer_flash': False}
    """An optional default data dictionary for user preferences."""

    supported_containers = HTML5Player.supported_containers \
                         | FlowPlayer.supported_containers
    supported_schemes = HTML5Player.supported_schemes \
                      | FlowPlayer.supported_schemes

    def __init__(self, media, uris, **kwargs):
        super(HTML5PlusFlowPlayer, self).__init__(media, uris, **kwargs)
        self.flowplayer = None
        self.prefer_flash = self.data.get('prefer_flash', False)
        self.uris = [u for u, p in izip(uris, AbstractHTML5Player.can_play(uris)) if p]
        flow_uris = [u for u, p in izip(uris, FlowPlayer.can_play(uris)) if p]
        if flow_uris:
            self.flowplayer = FlowPlayer(media, flow_uris, **kwargs)

    def render_js_player(self):
        flash = self.flowplayer and self.flowplayer.render_js_player()
        html5 = self.uris and super(HTML5PlusFlowPlayer, self).render_js_player()
        if html5 and flash:
            return Markup("new mcore.MultiPlayer([%s, %s])" % \
                (self.prefer_flash and (flash, html5) or (html5, flash)))
        if html5 or flash:
            return html5 or flash
        return None

    def render_markup(self, error_text=None):
        """Render the XHTML markup for this player instance.

        :param error_text: Optional error text that should be included in
            the final markup if appropriate for the player.
        :rtype: ``unicode`` or :class:`genshi.core.Markup`
        :returns: XHTML that will not be escaped by Genshi.

        """
        if self.uris:
            return super(HTML5PlusFlowPlayer, self).render_markup(error_text)
        return error_text or u''

AbstractHTML5Player.register(HTML5PlusFlowPlayer)

###############################################################################

class JWPlayer(AbstractHTML5Player):
    """
    JWPlayer (Flash)
    """
    name = u'jwplayer'
    """A unicode string identifier for this class."""

    display_name = N_(u'JWPlayer')
    """A unicode display name for the class, to be used in the settings UI."""

    supported_containers = AbstractHTML5Player.supported_containers \
                         | AbstractRTMPFlashPlayer.supported_containers \
                         | set(['xml', 'srt'])
#    supported_containers.add('youtube')
    supported_types = set([AUDIO, VIDEO, AUDIO_DESC, CAPTIONS])
    supported_schemes = set([HTTP, RTMP])

    # Height adjustment in pixels to accomodate the control bar and stay 16:9
    _height_diff = 24

    providers = {
        AUDIO: 'sound',
        VIDEO: 'video',
    }

    def __init__(self, media, uris, **kwargs):
        html5_uris = [uri
            for uri, p in izip(uris, AbstractHTML5Player.can_play(uris)) if p]
        flash_uris = [uri
            for uri, p in izip(uris, AbstractRTMPFlashPlayer.can_play(uris)) if p]
        super(JWPlayer, self).__init__(media, html5_uris, **kwargs)
        self.all_uris = uris
        self.flash_uris = flash_uris
        self.rtmp_uris = pick_uris(flash_uris, scheme=RTMP)

    def swf_url(self):
        return url_for('/scripts/third-party/jw_player/player.swf',
                       qualified=self.qualified)

    def js_url(self):
        return url_for('/scripts/third-party/jw_player/jwplayer.min.js',
                       qualified=self.qualified)

    def player_vars(self):
        """Return a python dict of vars for this player."""
        vars = {
            'autostart': self.autoplay,
            'height': self.adjusted_height,
            'width': self.adjusted_width,
            'controlbar': 'bottom',
            'players': [
                # XXX: Currently flash *must* come first for the RTMP/HTTP logic.
                {'type': 'flash', 'src': self.swf_url()},
                {'type': 'html5'},
                {'type': 'download'},
            ],
        }
        playlist = self.playlist()
        plugins = self.plugins()
        if playlist:
            vars['playlist'] = playlist
        if plugins:
            vars['plugins'] = plugins

        # Playlists have 'image's and <video> elements have provide 'poster's,
        # but <audio> elements have no 'poster' attribute. Set an image via JS:
        if self.media.type == AUDIO and not playlist:
            vars['image'] = thumb_url(self.media, 'l', qualified=self.qualified)

        return vars

    def playlist(self):
        if self.uris:
            return None

        if self.rtmp_uris:
            return self.rtmp_playlist()

        uri = self.flash_uris[0]
        return [{
            'image': thumb_url(self.media, 'l', qualified=self.qualified),
            'file': str(uri),
            'duration': self.media.duration,
            'provider': self.providers[uri.file.type],
        }]

    def rtmp_playlist(self):
        levels = []
        item = {'streamer': self.rtmp_uris[0].server_uri,
                'provider': 'rtmp',
                'levels': levels,
                'duration': self.media.duration}
        # If no HTML5 uris exist, no <video> tag will be output, so we have to
        # say which thumb image to use. Otherwise it's unnecessary bytes.
        if not self.uris:
            item['image'] = thumb_url(self.media, 'l', qualified=self.qualified)
        for uri in self.rtmp_uris:
            levels.append({
                'file': uri.file_uri,
                'bitrate': uri.file.bitrate,
                'width': uri.file.width,
            })
        playlist = [item]
        return playlist

    def plugins(self):
        plugins = {}
        audio_desc = pick_uris(self.all_uris, type=AUDIO_DESC)
        captions = pick_uris(self.all_uris, type=CAPTIONS)
        if audio_desc:
            plugins['audiodescription'] = {'file': str(audio_desc[0])}
        if captions:
            plugins['captions'] = {'file': str(captions[0])}
        return plugins

    def flash_override_playlist(self):
        # Use this hook only when HTML5 and RTMP uris exist.
        if self.uris and self.rtmp_uris:
            return self.rtmp_playlist()

    def render_js_player(self):
        vars = simplejson.dumps(self.player_vars())
        flash_playlist = simplejson.dumps(self.flash_override_playlist())
        return Markup("new mcore.JWPlayer(%s, %s)" % (vars, flash_playlist))

    def render_markup(self, error_text=None):
        """Render the XHTML markup for this player instance.

        :param error_text: Optional error text that should be included in
            the final markup if appropriate for the player.
        :rtype: ``unicode`` or :class:`genshi.core.Markup`
        :returns: XHTML that will not be escaped by Genshi.

        """
        if self.uris:
            html5_tag = super(JWPlayer, self).render_markup(error_text)
        else:
            html5_tag = ''
        script_tag = Markup(
            '<script type="text/javascript" src="%s"></script>' % self.js_url())
        return html5_tag + script_tag

AbstractHTML5Player.register(JWPlayer)

###############################################################################

class SublimePlayer(AbstractHTML5Player):
    """
    Sublime Video Player with a builtin flash fallback
    """
    name = u'sublime'
    """A unicode string identifier for this class."""

    display_name = N_(u'Sublime Video Player')
    """A unicode display name for the class, to be used in the settings UI."""

    settings_form_class = player_forms.SublimePlayerPrefsForm
    """An optional :class:`mediadrop.forms.admin.players.PlayerPrefsForm`."""

    default_data = {'script_tag': ''}
    """An optional default data dictionary for user preferences."""

    supported_types = set([VIDEO])
    """Sublime does not support AUDIO at this time."""

    supports_resizing = False
    """A flag that allows us to mark the few players that can't be resized.

    Setting this to False ensures that the resize (expand/shrink) controls will
    not be shown in our player control bar.
    """

    def html5_attrs(self):
        attrs = super(SublimePlayer, self).html5_attrs()
        attrs['class'] = (attrs.get('class', '') + ' sublime').strip()
        return attrs

    def render_js_player(self):
        return Markup('new mcore.SublimePlayer()')

    def render_markup(self, error_text=None):
        """Render the XHTML markup for this player instance.

        :param error_text: Optional error text that should be included in
            the final markup if appropriate for the player.
        :rtype: ``unicode`` or :class:`genshi.core.Markup`
        :returns: XHTML that will not be escaped by Genshi.

        """
        video_tag = super(SublimePlayer, self).render_markup(error_text)
        return video_tag + Markup(self.data['script_tag'])

AbstractHTML5Player.register(SublimePlayer)

###############################################################################

class iTunesPlayer(FileSupportMixin, AbstractPlayer):
    """
    A dummy iTunes Player that allows us to test if files :meth:`can_play`.
    """
    name = u'itunes'
    """A unicode string identifier for this class."""

    display_name = N_(u'iTunes Player')
    """A unicode display name for the class, to be used in the settings UI."""

    supported_containers = set(['mp3', 'mp4'])
    supported_schemes = set([HTTP])

###############################################################################

def preferred_player_for_media(media, **kwargs):
    uris = media.get_uris()

    from mediadrop.model.players import fetch_enabled_players
    # Find the first player that can play any uris
    for player_cls, player_data in fetch_enabled_players():
        can_play = player_cls.can_play(uris)
        if any(can_play):
            break
    else:
        return None

    # Grab just the uris that the chosen player can play
    playable_uris = [uri for uri, plays in izip(uris, can_play) if plays]
    kwargs['data'] = player_data
    return player_cls(media, playable_uris, **kwargs)


def media_player(media, is_widescreen=False, show_like=True, show_dislike=True,
                 show_download=False, show_embed=False, show_playerbar=True,
                 show_popout=True, show_resize=False, show_share=True,
                 js_init=None, **kwargs):
    """Instantiate and render the preferred player that can play this media.

    We make no effort to pick the "best" player here, we simply return
    the first player that *can* play any of the URIs associated with
    the given media object. It's up to the user to declare their own
    preferences wisely.

    Player preferences are fetched from the database and the
    :attr:`mediadrop.model.players.c.data` dict is passed as kwargs to
    :meth:`AbstractPlayer.__init__`.

    :type media: :class:`mediadrop.model.media.Media`
    :param media: A media instance to play.

    :param js_init: Optional function to call after the javascript player
        controller has been instantiated. Example of a function literal:
        ``function(controller){ controller.setFillScreen(true); }``.
        Any function reference can be used as long as it is defined
        in all pages and accepts the JS player controller as its first
        and only argument.

    :param \*\*kwargs: Extra kwargs for :meth:`AbstractPlayer.__init__`.

    :rtype: `str` or `None`
    :returns: A rendered player.
    """
    player = preferred_player_for_media(media, **kwargs)
    return render('players/html5_or_flash.html', {
        'player': player,
        'media': media,
        'uris': media.get_uris(),
        'is_widescreen': is_widescreen,
        'js_init': js_init,
        'show_like': show_like,
        'show_dislike': show_dislike,
        'show_download': show_download,
        'show_embed': show_embed,
        'show_playerbar': show_playerbar,
        'show_popout': show_popout,
        'show_resize': show_resize and (player and player.supports_resizing),
        'show_share': show_share,
    })

def pick_podcast_media_file(media):
    """Return a file playable in the most podcasting client: iTunes.

    :param media: A :class:`~mediadrop.model.media.Media` instance.
    :returns: A :class:`~mediadrop.model.media.MediaFile` object or None
    """
    uris = media.get_uris()
    for i, plays in enumerate(iTunesPlayer.can_play(uris)):
        if plays:
            return uris[i]
    return None

def pick_any_media_file(media):
    """Return a file playable in at least one of the configured players.

    :param media: A :class:`~mediadrop.model.media.Media` instance.
    :returns: A :class:`~mediadrop.model.media.MediaFile` object or None
    """
    uris = media.get_uris()
    from mediadrop.model.players import fetch_enabled_players
    for player_cls, player_data in fetch_enabled_players():
        for i, plays in enumerate(player_cls.can_play(uris)):
            if plays:
                return uris[i]
    return None

def update_enabled_players():
    """Ensure that the encoding status of all media is up to date with the new
    set of enabled players.

    The encoding status of Media objects is dependent on there being an
    enabled player that supports that format. Call this method after changing
    the set of enabled players, to ensure encoding statuses are up to date.
    """
    from mediadrop.model import DBSession, Media
    media = DBSession.query(Media)
    for m in media:
        m.update_status()

def embed_iframe(media, width=400, height=225, frameborder=0, **kwargs):
    """Return an <iframe> tag that loads our universal player.

    :type media: :class:`mediadrop.model.media.Media`
    :param media: The media object that is being rendered, to be passed
        to all instantiated player objects.
    :rtype: :class:`genshi.builder.Element`
    :returns: An iframe element stream.

    """
    src = url_for(controller='/media', action='embed_player', slug=media.slug,
                  qualified=True)
    tag = Element('iframe', src=src, width=width, height=height,
                  frameborder=frameborder, **kwargs)
    # some software is known not to work with self-closing iframe tags 
    # ('<iframe ... />'). Several WordPress instances are affected as well as
    # TWiki http://mediadrop.net/community/topic/embed-iframe-closing-tag
    tag.append('')
    return tag

embed_player = embed_iframe
