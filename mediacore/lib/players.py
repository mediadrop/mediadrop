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
import simplejson

from itertools import izip
from urllib import urlencode

from genshi.builder import Element
from genshi.core import Markup
from pylons import app_globals

from mediacore.lib.compat import any
from mediacore.lib.decorators import memoize
from mediacore.lib.filetypes import AUDIO, VIDEO, AUDIO_DESC, CAPTIONS
from mediacore.lib.templating import render
from mediacore.lib.thumbnails import thumb_url
from mediacore.lib.uri import StorageURI, pick_uris
from mediacore.lib.util import merge_dicts, url_for
#from mediacore.model.players import fetch_players XXX: Import at EOF
from mediacore.plugin import events
from mediacore.plugin.abc import AbstractClass, abstractmethod, abstractproperty
from mediacore.plugin.events import observes

log = logging.getLogger(__name__)

HTTP, RTMP = 'http', 'rtmp'

class PlayerError(Exception):
    pass

###############################################################################

class AbstractPlayer(AbstractClass):
    """
    Player Base Class that all players must implement.
    """

    name = abstractproperty()
    """A unicode string name for the class, to be used in the settings UI."""

    logical_types = abstractproperty()
    """The `set` of playback methods this player implements.

    The value of this is used only to differentiate it from other players,
    so that we can choose a fallback player that implements a different method.
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

    @abstractmethod
    def render(self, **kwargs):
        """Render this player instance.

        :param \*\*kwargs: Any extra options that modify how the render
            is done. All kwargs MUST be optional; provide sane defaults.
        :rtype: :class:`genshi.core.Markup`
        :returns: XHTML or javascript that will not be escaped by Genshi.

        """

    def __init__(self, media, uris, width=400, height=225,
                 autoplay=False, autobuffer=False, qualified=False, **kwargs):
        """Initialize the player with the media that it will be playing.

        :type media: :class:`mediacore.model.media.Media` instance
        :param media: The media object that will be rendered.
        :type uris: list
        :param uris: The StorageURIs this player has said it :meth:`can_play`.
        :type elem_id: unicode, None, Default
        :param elem_id: The element ID to use when rendering. If left
            undefined, a sane default value is provided. Use None to disable.

        """
        self.media = media
        self.uris = uris
        self.width = width
        self.height = height
        self.autoplay = autoplay
        self.autobuffer = autobuffer
        self.qualified = qualified
        self.elem_id = kwargs.pop('elem_id', '%s-player' % media.slug)

    _width_diff = 0
    _height_diff = 0

    @property
    def adjusted_width(self):
        return self.width + self._width_diff

    @property
    def adjusted_height(self):
        return self.height + self._height_diff

    def get_uris(self, **kwargs):
        return pick_uris(self.uris, **kwargs)

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

    def render(self, method=None, **kwargs):
        """Render this player instance.

        :param method: Select whether you want an 'embed' tag, an
            'object' tag, or a 'swiff' javascript snippet. If left empty,
            returns XHTML <object><embed /></object> tags.
        :rtype: :class:`genshi.core.Markup`
        :returns: XHTML or javascript that will not be escaped by Genshi.

        """
        if method is None:
            object = self.render_object(**kwargs)
            kwargs['id'] = None
            return object(self.render_embed(**kwargs))
        renderer = {
            'embed': self.render_embed,
            'object': self.render_object,
            'swiff': self.render_swiff,
        }.get(method)
        return renderer(**kwargs)

    def render_embed(self, **kwargs):
        elem_id = kwargs.pop('id', self.elem_id)
        swf_url = self.swf_url()
        flashvars = urlencode(self.flashvars())

        tag = Element('embed', type='application/x-shockwave-flash',
                      allowfullscreen='true', allowscriptaccess='always',
                      width=self.adjusted_width, height=self.adjusted_height,
                      src=swf_url, flashvars=flashvars, id=elem_id)
        return tag

    def render_object(self, **kwargs):
        elem_id = kwargs.pop('id', self.elem_id)
        swf_url = self.swf_url()
        flashvars = urlencode(self.flashvars())

        tag = Element('object', type='application/x-shockwave-flash',
                      width=self.adjusted_width, height=self.adjusted_height,
                      data=swf_url, id=elem_id)
        tag(Element('param', name='movie', value=swf_url))
        tag(Element('param', name='flashvars', value=flashvars))
        tag(Element('param', name='allowfullscreen', value='true'))
        tag(Element('param', name='allowscriptaccess', value='always'))
        return tag

    def render_swiff(self):
        """Render a MooTools Swiff javascript snippet.

        See: http://mootools.net/docs/core/Utilities/Swiff
        """
        params = {
            'width': self.adjusted_width,
            'height': self.adjusted_height,
            'params': {'allowfullscreen': 'true'},
            'vars': self.flashvars(),
        }
        params = simplejson.dumps(params)
        return Markup("new Swiff('%s', %s)" % (self.swf_url(), params))

###############################################################################

class AbstractFlashPlayer(FileSupportMixin, FlashRenderMixin, AbstractPlayer):
    """
    Base Class for standard Flash Players.

    This does not include flash players from other vendors (embed types),
    but we may want to change that after the storage engine architecture
    has been implemented.

    """
    logical_types = set(['flash'])
    supported_containers = set(['mp3', 'mp4', 'flv', 'flac'])

    @abstractmethod
    def flashvars(self):
        """Return a python dict of flashvars for this player."""

    @abstractmethod
    def swf_url(self):
        """Return the flash player URL."""


class FlowPlayer(AbstractFlashPlayer):
    """
    FlowPlayer (Flash)
    """
    name = 'flowplayer'

    supported_schemes = set([HTTP])

    def swf_url(self):
        """Return the flash player URL."""
        return url_for('/scripts/third-party/flowplayer-3.2.3.swf',
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


class JWPlayer(AbstractFlashPlayer):
    """
    JWPlayer (Flash)
    """
    name = 'jwplayer'

    supported_containers = AbstractFlashPlayer.supported_containers
#    supported_containers.add('youtube')
    supported_types = set([AUDIO, VIDEO, AUDIO_DESC, CAPTIONS])
    supported_schemes = set([HTTP, RTMP])

    providers = {
        AUDIO: 'sound',
        VIDEO: 'video',
    }

    # Height adjustment in pixels to accomodate the control bar and stay 16:9
    _height_diff = 24

    def swf_url(self):
        """Return the flash player URL."""
        return url_for('/scripts/third-party/jw_player/player.swf',
                       qualified=self.qualified)

    def flashvars(self):
        """Return a python dict of flashvars for this player."""
        youtube = self.get_uris(container='youtube')
        rtmp = self.get_uris(scheme=RTMP)
        http = self.get_uris(scheme=HTTP)
        audio_desc = self.get_uris(type=AUDIO_DESC)
        captions = self.get_uris(type=CAPTIONS)

        vars = {
            'image': thumb_url(self.media, 'l', qualified=self.qualified),
            'autostart': self.autoplay,
        }
        if youtube:
            vars['provider'] = 'youtube'
            vars['file'] = str(youtube[0])
        elif rtmp:
            if len(rtmp) > 1:
                # For multiple RTMP bitrates, use Media RSS playlist
                vars = {}
                vars['playlistfile'] = url_for(
                    controller='/media',
                    action='jwplayer_rtmp_mrss',
                    slug=self.media.slug,
                )
            else:
                # For a single RTMP stream, use regular Flash vars.
                rtmp_uri = rtmp[0]
                vars['file'] = rtmp_uri.file_uri
                vars['streamer'] = rtmp_uri.server_uri
            vars['provider'] = 'rtmp'
        else:
            http_uri = http[0]
            vars['provider'] = self.providers[http_uri.file.type]
            vars['file'] = str(http_uri)

        plugins = []
        if rtmp:
            plugins.append('rtmp')
        if audio_desc:
            plugins.append('audiodescription');
            vars['audiodescription.file'] = audio_desc[0].uri
        if captions:
            plugins.append('captions');
            vars['captions.file'] = captions[0].uri
        if plugins:
            vars['plugins'] = ','.join(plugins)

        return vars

AbstractFlashPlayer.register(JWPlayer)

###############################################################################

class AbstractEmbedPlayer(AbstractPlayer):

    scheme = abstractproperty()

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


class VimeoUniversalEmbedPlayer(AbstractEmbedPlayer):
    """
    Vimeo Universal Player
    """

    name = scheme = 'vimeo'
    logical_types = set(['flash', 'html5'])

    def render(self, **kwargs):
        uri = self.uris[0]
        tag = Element('iframe', src=uri, frameborder=0,
                      width=self.adjusted_width, height=self.adjusted_height)
        return tag

AbstractEmbedPlayer.register(VimeoUniversalEmbedPlayer)


class AbstractFlashEmbedPlayer(FlashRenderMixin, AbstractEmbedPlayer):

    logical_types = set(['flash'])

    def swf_url(self):
        """Return the flash player URL."""
        return str(self.uris[0])

    def flashvars(self):
        """Return a python dict of flashvars for this player."""
        return {}


class YouTubeFlashPlayer(AbstractFlashEmbedPlayer):

    name = scheme = 'youtube'
    _height_diff = 25
    is_youtube = True

AbstractFlashEmbedPlayer.register(YouTubeFlashPlayer)


class GoogleVideoFlashPlayer(AbstractFlashEmbedPlayer):

    name = scheme = 'googlevideo'
    _height_diff = 27

AbstractFlashEmbedPlayer.register(GoogleVideoFlashPlayer)

class BlipTVFlashPlayer(AbstractFlashEmbedPlayer):

    name = scheme = 'bliptv'

AbstractFlashEmbedPlayer.register(BlipTVFlashPlayer)

###############################################################################

class AbstractHTML5Player(FileSupportMixin, AbstractPlayer):
    """HTML5 <audio> / <video> tag.

    References:

        - http://dev.w3.org/html5/spec/Overview.html#audio
        - http://dev.w3.org/html5/spec/Overview.html#video
        - http://developer.apple.com/safari/library/documentation/AudioVideo/Conceptual/Using_HTML5_Audio_Video/Introduction/Introduction.html

    """
    logical_types = set(['html5'])
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

    def render(self):
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
        return tag


class HTML5Player(AbstractHTML5Player):
    """HTML5 Player Implementation.

    Seperated from :class:`AbstractHTML5Player` to make it easier to subclass
    and provide a custom HTML5 player.

    """
    name = 'html5'

AbstractHTML5Player.register(HTML5Player)

###############################################################################

class iTunesPlayer(FileSupportMixin, AbstractPlayer):
    """
    A dummy iTunes Player that allows us to test if files :meth:`can_play`.

    """
    name = 'itunes'
    logical_types = set(['podcast'])
    supported_containers = set(['mp3', 'mp4'])
    supported_schemes = set([HTTP])

    def render(self, **kwargs):
        raise NotImplementedError('iTunesPlayer cannot be rendered.')

###############################################################################

def media_player(media, **kwargs):
    """Instantiate and return the preferred player that can play this media.

    We make no effort to pick the "best" player here, we simply return
    the first player that *can* play any of the URIs associated with
    the given media object. It's up to the user to declare their own
    preferences wisely.

    Player preferences are fetched from the database and the
    :attr:`mediacore.model.players.c.data` dict is passed as kwargs to
    :meth:`AbstractPlayer.__init__`.

    :type media: :class:`mediacore.model.media.Media`
    :param media: A media instance to play.
    :param \*\*kwargs: Extra kwargs for :meth:`AbstractPlayer.__init__`.
    :rtype: :class:`AbstractPlayer` or `None`
    :returns: An instantiated player object. To render, you must
        explicitly call :meth:`AbstractPlayer.render`.
    """
    uris = media.get_uris()

    # Find the first player that can play any uris
    for player_cls, player_prefs in fetch_enabled_players():
        can_play = player_cls.can_play(uris)
        if any(can_play):
            break
    else:
        return None

    # Grab just the uris that the chosen player can play
    playable_uris = [uri for uri, plays in izip(uris, can_play) if plays]

    # Create a new kwargs dict for the player object using the data dict
    # from the database + the kwargs called here.
    player_kwargs = {}
    merge_dicts(player_kwargs, player_prefs, kwargs)

    return player_cls(media, playable_uris, **player_kwargs)

def pick_podcast_media_file(media):
    """Return a file playable in the most podcasting client: iTunes.

    :param media: A :class:`~mediacore.model.media.Media` instance.
    :returns: A :class:`~mediacore.model.media.MediaFile` object or None
    """
    uris = media.get_uris()
    for i, plays in enumerate(iTunesPlayer.can_play(uris)):
        if plays:
            return uris[i]
    return None

def pick_any_media_file(media):
    """Return a file playable in at least one of the configured players.

    :param media: A :class:`~mediacore.model.media.Media` instance.
    :returns: A :class:`~mediacore.model.media.MediaFile` object or None
    """
    uris = media.get_uris()
    for player_cls, player_prefs in fetch_enabled_players():
        for i, plays in enumerate(player_cls.can_play(uris)):
            if plays:
                return uris[i]
    return None

def embed_iframe(media, width=400, height=225, frameborder=0, **kwargs):
    """Return an <iframe> tag that loads our universal player.

    :type media: :class:`mediacore.model.media.Media`
    :param media: The media object that is being rendered, to be passed
        to all instantiated player objects.
    :rtype: :class:`genshi.builder.Element`
    :returns: An iframe element stream.

    """
    src = url_for(controller='/media', action='embed_player', slug=media.slug,
                  qualified=True)
    tag = Element('iframe', src=src, width=width, height=height,
                  frameborder=frameborder, **kwargs)
    return tag

embed_player = embed_iframe

from mediacore.model.players import fetch_enabled_players
