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
from pylons.i18n import N_

from mediacore.forms.admin import players as player_forms
from mediacore.lib.compat import any
from mediacore.lib.filetypes import AUDIO, VIDEO, AUDIO_DESC, CAPTIONS
from mediacore.lib.templating import render
from mediacore.lib.thumbnails import thumb_url
from mediacore.lib.uri import pick_uris
from mediacore.lib.util import url_for
#from mediacore.model.players import fetch_players XXX: Import at EOF
from mediacore.plugin.abc import AbstractClass, abstractmethod, abstractproperty

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
    """An optional :class:`mediacore.forms.admin.players.PlayerPrefsForm`."""

    default_data = {}
    """An optional default data dictionary for user preferences."""

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

    def __init__(self, media, uris, data=None, width=400, height=225,
                 autoplay=False, autobuffer=False, qualified=False, **kwargs):
        """Initialize the player with the media that it will be playing.

        :type media: :class:`mediacore.model.media.Media` instance
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
        """Return the desired viewable width + any extra for the player."""
        return self.width + self._width_diff

    @property
    def adjusted_height(self):
        """Return the desired viewable height + the height of the controls."""
        return self.height + self._height_diff

    def get_uris(self, **kwargs):
        """Return a subset of the :attr:`uris` for this player.

        This allows for easy filtering of URIs by feeding any number of
        kwargs to this function. See :func:`mediacore.lib.uri.pick_uris`.

        """
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

    This does not typically include flash players from other vendors
    such as embed types.

    """
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
    name = u'flowplayer'
    """A unicode string identifier for this class."""

    display_name = N_(u'Flowplayer')
    """A unicode display name for the class, to be used in the settings UI."""

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
    name = u'jwplayer'
    """A unicode string identifier for this class."""

    display_name = N_(u'JWPlayer')
    """A unicode display name for the class, to be used in the settings UI."""

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
            plugins.append('audiodescription')
            vars['audiodescription.file'] = audio_desc[0].uri
        if captions:
            plugins.append('captions')
            vars['captions.file'] = captions[0].uri
        if plugins:
            vars['plugins'] = ','.join(plugins)

        return vars

AbstractFlashPlayer.register(JWPlayer)

###############################################################################

class AbstractEmbedPlayer(AbstractPlayer):
    """
    Abstract Embed Player for third-party services like YouTube

    Typically embed players will play only their own content, and that is
    the only way such content can be played. Therefore each embed type has
    been given its own :attr:`~mediacore.lib.uri.StorageURI.scheme` which
    uniquely identifies it.

    For example, :meth:`mediacore.lib.storage.YoutubeStorage.get_uris`
    returns URIs with a scheme of `'youtube'`, and the special
    :class:`YoutubePlayer` would overload :attr:`scheme` to also be
    `'youtube'`. This would allow the Youtube player to play those URIs.

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


class VimeoUniversalEmbedPlayer(AbstractEmbedPlayer):
    """
    Vimeo Universal Player

    This simple player handles media with files that stored using
    :class:`mediacore.lib.storage.VimeoStorage`.

    This player has seamless HTML5 and Flash support.

    """
    name = u'vimeo'
    """A unicode string identifier for this class."""

    display_name = N_(u'Vimeo')
    """A unicode display name for the class, to be used in the settings UI."""

    scheme = u'vimeo'
    """The `StorageURI.scheme` which uniquely identifies this embed type."""

    def render(self, **kwargs):
        uri = self.uris[0]
        tag = Element('iframe', src=uri, frameborder=0,
                      width=self.adjusted_width, height=self.adjusted_height)
        return tag

AbstractEmbedPlayer.register(VimeoUniversalEmbedPlayer)


class DailyMotionEmbedPlayer(AbstractEmbedPlayer):
    """
    Daily Motion Universal Player

    This simple player handles media with files that stored using
    :class:`mediacore.lib.storage.DailyMotionStorage`.

    This player has seamless HTML5 and Flash support.

    """
    name = u'dailymotion'
    """A unicode string identifier for this class."""

    display_name = N_(u'Daily Motion')
    """A unicode display name for the class, to be used in the settings UI."""

    scheme = u'dailymotion'
    """The `StorageURI.scheme` which uniquely identifies this embed type."""

    def render(self, **kwargs):
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
        return tag

AbstractEmbedPlayer.register(DailyMotionEmbedPlayer)


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


class YoutubeFlashPlayer(AbstractFlashEmbedPlayer):
    """
    YouTube Player

    This simple player handles media with files that stored using
    :class:`mediacore.lib.storage.YoutubeStorage`.

    """
    name = u'youtube'
    """A unicode string identifier for this class."""

    display_name = N_(u'YouTube')
    """A unicode display name for the class, to be used in the settings UI."""

    scheme = u'youtube'
    """The `StorageURI.scheme` which uniquely identifies this embed type."""

    _height_diff = 25

AbstractFlashEmbedPlayer.register(YoutubeFlashPlayer)


class GoogleVideoFlashPlayer(AbstractFlashEmbedPlayer):
    """
    Google Video Player

    This simple player handles media with files that stored using
    :class:`mediacore.lib.storage.GoogleVideoStorage`.

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
    :class:`mediacore.lib.storage.BlipTVStorage`.

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
    """An optional :class:`mediacore.forms.admin.players.PlayerPrefsForm`."""

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

    def render(self, **kwargs):
        if self.uris:
            html5_tag = super(HTML5PlusFlowPlayer, self).render(**kwargs)
        else:
            html5_tag = None
        return render('players/html5_or_flash.html', {
            'player': self,
            'html5': html5_tag,
            'flash': self.flowplayer,
            'prefer_flash': self.prefer_flash and self.flowplayer,
        })

AbstractHTML5Player.register(HTML5PlusFlowPlayer)

class HTML5PlusJWPlayer(AbstractHTML5Player):
    """
    HTML5 Player with fallback to JWPlayer.

    .. note::

        Although this class duplicates much of the functionality in
        :class:`HTML5PlusFlowPlayer` we are not going to worry about
        that since the soon-to-be-integrated JWPlayer 5.3 seamlessly
        includes both an HTML5 and a Flash player.

    """
    name = u'html5+jwplayer'
    """A unicode string identifier for this class."""

    display_name = N_(u'HTML5 + JWPlayer Fallback')
    """A unicode display name for the class, to be used in the settings UI."""

    settings_form_class = player_forms.HTML5OrFlashPrefsForm
    """An optional :class:`mediacore.forms.admin.players.PlayerPrefsForm`."""

    default_data = {'prefer_flash': False}
    """An optional default data dictionary for user preferences."""

    supported_containers = HTML5Player.supported_containers \
                         | JWPlayer.supported_containers
    supported_schemes = HTML5Player.supported_schemes \
                      | JWPlayer.supported_schemes

    def __init__(self, media, uris, **kwargs):
        super(HTML5PlusJWPlayer, self).__init__(media, uris, **kwargs)
        self.jwplayer = None
        self.prefer_flash = self.data.get('prefer_flash', False)
        self.uris = [u for u, p in izip(uris, AbstractHTML5Player.can_play(uris)) if p]
        jw_uris = [u for u, p in izip(uris, JWPlayer.can_play(uris)) if p]
        if jw_uris:
            self.jwplayer = JWPlayer(media, jw_uris, **kwargs)

    def render(self, **kwargs):
        if self.uris:
            html5_tag = super(HTML5PlusJWPlayer, self).render(**kwargs)
        else:
            html5_tag = None
        return render('players/html5_or_flash.html', {
            'player': self,
            'html5': html5_tag,
            'flash': self.jwplayer,
            'prefer_flash': self.prefer_flash and self.jwplayer,
        })

AbstractHTML5Player.register(HTML5PlusJWPlayer)

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
    """An optional :class:`mediacore.forms.admin.players.PlayerPrefsForm`."""

    default_data = {'script_tag': ''}
    """An optional default data dictionary for user preferences."""

    def html5_attrs(self):
        attrs = super(SublimePlayer, self).html5_attrs()
        attrs['class'] = (attrs.get('class', '') + ' sublime').strip()
        return attrs

    def render(self, **kwargs):
        video_tag = super(SublimePlayer, self).render(**kwargs)
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

    def render(self, **kwargs):
        raise NotImplementedError('iTunesPlayer cannot be rendered.')

###############################################################################

def media_player(media, **kwargs):
    """Instantiate and render the preferred player that can play this media.

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
    :rtype: `str` or `None`
    :returns: A rendered player.
    """
    uris = media.get_uris()

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
    player = player_cls(media, playable_uris, **kwargs)
    return player.render()

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
    for player_cls, player_data in fetch_enabled_players():
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
