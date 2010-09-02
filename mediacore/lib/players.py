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

import simplejson as json

from pylons import app_globals, config, request

from mediacore.lib.compat import namedtuple
from mediacore.lib.embedtypes import external_embedded_containers
from mediacore.lib.filetypes import (AUDIO, VIDEO, AUDIO_DESC, CAPTIONS,
    flash_supported_browsers, flash_supported_containers,
    native_supported_types, parse_user_agent_version)
from mediacore.lib.thumbnails import thumb_url

# TODO: This should probably be returned by parse_user_agent_version
#       when time permits. For now it's good enough to have it here so
#       at least the public API in templates is more readable.
Browser = namedtuple('Browser', 'name version')

class Player(object):
    """Abstract Player Class"""
    is_flash = False
    is_embed = False
    is_html5 = False

    supports_rtmp = False
    supports_http = False

    _width_diff = 0
    _height_diff = 0

    def __init__(self, media, files, browser, width=400, height=225,
                 autoplay=False, autobuffer=False, qualified=False,
                 fallback=None):
        self.media = media
        self.file = files[0]
        self.files = files
        self.browser = Browser(name=browser[0], version=browser[1])
        self.width = width
        self.height = height
        self.autoplay = autoplay
        self.autobuffer = autobuffer
        self.qualified = qualified
        self.fallback = fallback

    def update(self, **kwargs):
        for key, value in kwargs.iteritems():
            # Throw an exception if given an unrecognized key
            getattr(self, key)
            setattr(self, key, value)

    def include(self):
        return ''

    @property
    def adjusted_width(self):
        return self.width + self._width_diff

    @property
    def adjusted_height(self):
        return self.height + self._height_diff

    @property
    def elem_id(self):
        return '%s-%s-player' % (self.media.slug, self.file.id)

class FlowPlayer(Player):
    """Flash-based FlowPlayer"""
    is_flash = True
    supports_http = True

    def swf_url(self):
        from mediacore.lib.helpers import url_for
        return url_for('/scripts/third-party/flowplayer-3.2.3.swf', qualified=self.qualified)

    def flashvars(self):
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
            'url': self.file.play_url(qualified=self.qualified),
            'autoPlay': self.autoplay,
            'autoBuffer': self.autoplay or self.autobuffer,
        })

        # Flowplayer wants these options passed as an escaped JSON string
        # inside a single 'config' flashvar. When using the flowplayer's
        # own JS, this is automatically done, but since we use Swiff, a
        # SWFObject clone, we have to do this ourselves.
        vars = {'config': json.dumps(vars, separators=(',', ':'))}
        return vars

class JWPlayer(Player):
    """Flash-based JWPlayer -- this can play YouTube videos!"""
    is_flash = True
    supports_http = True
    supports_rtmp = True
    providers = {
        AUDIO: 'sound',
        VIDEO: 'video',
    }

    # Height adjustment in pixels to accomodate the control bar and stay 16:9
    _height_diff = 24

    def is_youtube_on_ipod(self):
        """Return True if this player instance is for YouTube video on an iDevice.

        In this case we render <object><embed /></object> tags so the
        iDevice's special handling of YouTube videos will work.
        """
        return self.file.container == 'youtube' \
            and self.browser[0] == 'iphone-ipod-ipad'

    @property
    def is_embed(self):
        return self.is_youtube_on_ipod()

    def swf_url(self):
        if self.is_youtube_on_ipod():
            return self.file.play_url(qualified=self.qualified)
        from mediacore.lib.helpers import url_for
        return url_for('/scripts/third-party/jw_player/player.swf', qualified=self.qualified)

    def flashvars(self):
        if self.is_youtube_on_ipod():
            return {}

        youtube = self.file.container == 'youtube'
        rtmp = self.file.is_rtmp
        audio_desc = self.media.audio_desc
        captions = self.media.captions

        vars = {
            'image': thumb_url(self.media, 'l', qualified=self.qualified),
            'autostart': self.autoplay,
        }
        if youtube:
            vars['provider'] = 'youtube'
            vars['file'] = self.file.link_url(qualified=self.qualified)
        elif rtmp:
            if len(self.files) > 1:
                # For multiple RTMP bitrates, use Media RSS playlist
                vars = {}
                from mediacore.lib.helpers import url_for
                vars['playlistfile'] = url_for(
                    controller='/media',
                    action='jwplayer_rtmp_mrss',
                    slug=self.media.slug,
                    ids=[f.id for f in self.files]
                )
            else:
                # For a single RTMP stream, use regular Flash vars.
                vars['file'] = self.file.rtmp_file_name
                vars['streamer'] = self.file.rtmp_stream_url
            vars['provider'] = 'rtmp'
        else:
            vars['provider'] = self.providers[self.file.type]
            vars['file'] = self.file.play_url(qualified=self.qualified)

        plugins = []
        if rtmp:
            plugins.append('rtmp')
        if audio_desc:
            plugins.append('audiodescription');
            vars['audiodescription.file'] = audio_desc.play_url(qualified=self.qualified)
        if captions:
            plugins.append('captions');
            vars['captions.file'] = captions.play_url(qualified=self.qualified)
        if plugins:
            vars['plugins'] = ','.join(plugins)

        return vars

class EmbedPlayer(Player):
    """Generic third-party embed player.

    YouTube, Vimeo and Google Video can all be embedded in the same way.
    """
    is_embed = True
    is_flash = True

    # Height adjustment in pixels to accomodate the control bar and stay 16:9
    _height_diffs = {
        'youtube': 25,
        'google': 27,
    }

    @property
    def _height_diff(self):
        return self._height_diffs.get(self.file.container, 0)

    def swf_url(self):
        return self.file.play_url(qualified=self.qualified)

    def flashvars(self):
        return {}

class HTML5Player(Player):
    """HTML5 <audio> / <video> tag.

    References:

        - http://dev.w3.org/html5/spec/Overview.html#audio
        - http://dev.w3.org/html5/spec/Overview.html#video
        - http://developer.apple.com/safari/library/documentation/AudioVideo/Conceptual/Using_HTML5_Audio_Video/Introduction/Introduction.html

    """
    is_html5 = True
    supports_http = True

    def html5_attrs(self):
        attrs = {
            'src': self.file.play_url(qualified=self.qualified),
            'controls': 'controls',
        }
        if self.autoplay:
            attrs['autoplay'] = 'autoplay'
        elif self.autobuffer:
            # This isn't included in the HTML5 spec, but Safari supports it
            attrs['autobuffer'] = 'autobuffer'
        if self.file.type == VIDEO:
            attrs['poster'] = thumb_url(self.media, 'l', qualified=self.qualified)
        return attrs

class JWPlayerHTML5(HTML5Player):
    """HTML5-based JWPlayer

    XXX: This player cannot be chosen through the admin settings UI. We
         consider it to be too buggy for proper inclusion in this release,
         but have left it here in case anyone would like to use it anyway.
         Hopefully with time the bugs will be worked out and this code will
         become more useful.

    """
    def include(self):
        from mediacore.lib.helpers import url_for
        jquery = url_for('/scripts/third-party/jQuery-1.4.2-compressed.js', qualified=self.qualified)
        jwplayer = url_for('/scripts/third-party/jw_player/html5/jquery.jwplayer-compressed.js', qualified=self.qualified)
        skin = url_for('/scripts/third-party/jw_player/html5/skin/five.xml', qualified=self.qualified)
        include = """
<script type="text/javascript" src="%s"></script>
<script type="text/javascript" src="%s"></script>
<script type="text/javascript">
    jQuery('#%s').jwplayer({
        skin:'%s'
    });
</script>""" % (jquery, jwplayer, self.elem_id, skin)
        return include

    def html5_attrs(self):
        # We don't want the default controls to display. We'll use the JW controls.
        attrs = super(JWPlayerHTML5, self).html5_attrs()
        del attrs['controls']
        return attrs

class ZencoderVideoJSPlayer(HTML5Player):
    """HTML5 "VideoJS" Player by Zencoder

    XXX: This player cannot be chosen through the admin settings UI. We
         consider it to be too buggy for proper inclusion in this release,
         but have left it here in case anyone would like to use it anyway.
         Hopefully with time the bugs will be worked out and this code will
         become more useful.

    """
    def html5_attrs(self):
        attrs = super(ZencoderVideoJSPlayer, self).html5_attrs()
        if self.media.type == VIDEO:
            attrs['class'] = (attrs.get('class', '') + ' video-js').strip()
            for file in self.media.files:
                if file.type == CAPTIONS and file.container == 'srt':
                    attrs['data-subtitles'] = file.play_url(qualified=self.qualified)
                    break
        return attrs

    def include(self):
        if self.media.type != VIDEO:
            return ''
        from mediacore.lib.helpers import url_for
        js = url_for('/scripts/third-party/zencoder-video-js/video-yui-compressed.js', qualified=self.qualified)
        css = url_for('/scripts/third-party/zencoder-video-js/video-js.css', qualified=self.qualified)
        include = """
<script type="text/javascript" src="%s"></script>
<link rel="stylesheet" href="%s" type="text/css" media="screen" />
<script type="text/javascript">
    window.addEvent('domready', function(){
        var media = $('%s');
        var wrapper = new Element('div', {'class': 'video-js-box'}).wraps(media);
        var vjs = new VideoJS(media);
    });
</script>""" % (js, css, self.elem_id)
        return include

players = {
    'flowplayer': FlowPlayer,
    'jwplayer': JWPlayer,
    'jwplayer-html5': JWPlayerHTML5,
    'youtube': EmbedPlayer,
    'google': EmbedPlayer,
    'vimeo': EmbedPlayer,
    'html5': HTML5Player,
    'sublime': HTML5Player,
    'zencoder-video-js': ZencoderVideoJSPlayer,
}
"""Maps player names to classes that describe their behaviour.

The names are from the html5_player and flash_player settings.

You can use set 'youtube' to JWPlayer to take advantage of YouTube's
chromeless player. The only catch is that it doesn't support HD.
"""

def ordered_playable_files(files):
    """Return a sorted list of AUDIO and VIDEO files.

    The list will first contain all VIDEO files, sorted by size (decreasing),
    then all AUDIO files, sorted by size (decreasing).

    The returned list of files is thus in order of decreasing media-richness.
    """
    # Sort alphabetically
    files = sorted(files, key=lambda file: file.container)
    # Split by type
    video_files = [file for file in files if file.type == VIDEO]
    audio_files = [file for file in files if file.type == AUDIO]
    # Sort each type by filesize
    video_files.sort(key=lambda file: file.size, reverse=True)
    audio_files.sort(key=lambda file: file.size, reverse=True)
    # Done. Join and return the new, sorted list.
    return video_files + audio_files

def pick_media_file_player(media, browser=None, version=None, user_agent=None,
        player_type=None, include_embedded=True, **player_kwargs):
    """Return the best choice of files to play and which player to use.

    XXX: This method uses the very unsophisticated technique of assuming
         that if the client is capplayer_able of playing the container format, then
         the client should be able to play the tracks within the container,
         regardless of the codecs actually used. As such, admins would be
         well advised to use the lowest-common-denominator for their targeted
         clients when using files for consumption in an HTML5 player, and
         to use the standard codecs when encoding for Flash player use.

    :param media: A :class:`~mediacore.model.media.Media` instance.
    :param browser: Optional browser name to bypass user agents altogether.
        See :attr:`native_browser_supported_containers` for possible values.
    :type browser: str or None
    :param version: Optional version number, used when a browser arg is given.
    :type version: float or None
    :param user_agent: Optional User-Agent header to use. Defaults to
        that of the current request.
    :type user_agent: str or None
    :param player_type: Optional override value for the player_type setting.
    :type player_type: str or None
    :param include_embedded: Whether or not to include embedded players.
    :type include_embedded: bool
    :returns: A :class:`~mediacore.lib.players.Player` instance or None
    :rtype: tuple
    """
    files = ordered_playable_files(media.files)
    if not files:
        return None

    if browser is None:
        browser, version = parse_user_agent_version(user_agent)

    if player_type is None:
        player_type = app_globals.settings['player_type']

    browser_supports_flash = browser in flash_supported_browsers
    html5_supported_containers = [
        container
        for container, codecs
        in native_supported_types(browser, version)
    ]

    def get_playable_files(supported_containers):
        playable_files = [file for file in files if file.container in supported_containers]
        rtmp_playable_files = [file for file in playable_files if file.is_rtmp]
        http_playable_files = [file for file in playable_files if not file.is_rtmp]
        return rtmp_playable_files, http_playable_files

    def get_files_player(player, rtmp_playable_files, http_playable_files):
        """Return a list of playable MediaFile objects (or None) and an associated Player subclass (or None).

        The list will contain only RTMP files if possible, and only HTTP files otherwise."""
        if player:
            if player.supports_rtmp and rtmp_playable_files:
                return rtmp_playable_files, player
            elif player.supports_http and http_playable_files:
                return http_playable_files, player
        return None, None

    def get_html5_player():
        """Return a list of MediaFile objects and an associated HTML5 Player."""
        player = players[html5_player]
        rtmp_playable_files, http_playable_files = get_playable_files(html5_supported_containers)
        return get_files_player(player, rtmp_playable_files, http_playable_files)

    def get_flash_player():
        """Return a list of MediaFile objects and an associated Flash Player."""
        if browser_supports_flash:
            player = players[flash_player]
            rtmp_playable_files, http_playable_files = get_playable_files(flash_supported_containers)
            return get_files_player(player, rtmp_playable_files, http_playable_files)
        return None, None

    def get_embedded_player():
        """Return a list of MediaFile objects and an associated Embedded Player"""
        # We don't really track rtmp, http, or alternative files for embedded
        # videos. Playback is based on the MediaFile.embed field.
        # This method will just return the first embeddable file and its player
        useless_files, playable_files = get_playable_files(external_embedded_containers)
        if playable_files:
            playable_files = playable_files[:1]
            player = players[playable_files[0].container]
            return playable_files, player
        return None, None

    html5_player = app_globals.settings['html5_player']
    flash_player = app_globals.settings['flash_player']

    chosen_files, player = None, None
    ef_files, ef_player = None, None
    eh_files, eh_player = None, None

    if player_type == 'html5':
        chosen_files, player = get_html5_player()

    elif player_type == 'best':
        # Prefer embedded videos with a HTML5 player
        # FIXME: Ignores client browser support for HTML5.
        if include_embedded:
            chosen_files, player = get_embedded_player()
            if player is not None and not player.is_html5:
                ef_files, ef_player = chosen_files, player
                chosen_files, player = None, None

        # Fall back to hosted videos with an HTML5 player
        if player is None:
            chosen_files, player = get_html5_player()

        # Fall back to embedded videos with a Flash player
        if player is None \
        and include_embedded \
        and browser_supports_flash:
            chosen_files, player = ef_files, ef_player

        # Fall back to hosted videos with a Flash player
        if player is None:
            chosen_files, player = get_flash_player()

        # Fall back to embedded videos with a Flash player, even if the
        # client browser doesn't support Flash. This ignorance is a last ditch
        # effort to allow devices to specially handle YouTube, Vimeo, et al.
        # e.g. It allows iPhones to display YouTube videos.
        if player is None and include_embedded:
            chosen_files, player = ef_files, ef_player

    elif player_type == 'flash':
        # Prefer embedded videos with a Flash player
        if include_embedded:
            chosen_files, player = get_embedded_player()
            if player is not None:
                if player.is_flash and not browser_supports_flash:
                    ef_files, ef_player = chosen_files, player
                    chosen_files, player = None, None
                elif not player.is_flash:
                    eh_files, eh_player = chosen_files, player
                    chosen_files, player = None, None

        # Fall back to hosted videos with a Flash player
        if player is None:
            chosen_files, player = get_flash_player()

        # Fall back to embedded videos with an HTML5 player
        # FIXME: Ignores client browser support for HTML5.
        if player is None and include_embedded:
            chosen_files, player = eh_files, eh_player

        # Fall back to hosted videos with an HTML5 player
        if player is None:
            chosen_files, player = get_html5_player()

        # Fall back to embedded videos with a Flash player, even if the
        # client browser doesn't support Flash. This ignorance is a last ditch
        # effort to allow devices to specially handle YouTube, Vimeo, et al.
        # e.g. It allows iPhones to display YouTube videos.
        if player is None and include_embedded:
            chosen_files, player = ef_files, ef_player

    if player is None:
        return None

    # Pick a player to fail over to inside the browser, if decoding fails.
    fallback = None
    if 'fallback' in player_kwargs:
        fallback = player_kwargs.pop('fallback')
    elif player_type != 'html5':
        if player.is_html5:
            fallback = players[flash_player]
        elif player.is_flash:
            fallback = players[html5_player]

    # Instantiate the players
    player_args = (media, chosen_files, (browser, version))
    if fallback:
        player_kwargs['fallback'] = fallback(*player_args, **player_kwargs)
    player_obj = player(*player_args, **player_kwargs)

    return player_obj
