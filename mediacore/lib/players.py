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

from mediacore.lib.embedtypes import external_embedded_containers
from mediacore.lib.filetypes import (AUDIO, VIDEO, AUDIO_DESC, CAPTIONS,
    flash_supported_browsers, flash_supported_containers,
    native_supported_types, parse_user_agent_version)
from mediacore.lib.thumbnails import thumb_url


class Player(object):
    """Abstract Player Class"""
    is_flash = False
    is_embed = False
    is_html5 = False

    def __init__(self, media, file, browser, width=400, height=225,
                 autoplay=False, autobuffer=False, qualified=False,
                 fallback=None):
        self.media = media
        self.file = file
        self.browser = browser
        self.width = width
        self.height = height
        self.autoplay = autoplay
        self.autobuffer = autobuffer
        self.qualified = qualified
        self.fallback = fallback

    def include(self):
        return ''

    def update(self, **kwargs):
        for key, value in kwargs.iteritems():
            # Throw an exception if given an unrecognized key
            getattr(self, key)
            setattr(self, key, value)

    @property
    def adjusted_width(self):
        return self.width

    @property
    def adjusted_height(self):
        return self.height + player_controls_heights.get(self.__class__, 0)

    @property
    def elem_id(self):
        return '%s-%s-player' % (self.media.slug, self.file.id)

class FlowPlayer(Player):
    """Flash-based FlowPlayer"""
    is_flash = True

    def swf_url(self):
        from mediacore.lib.helpers import url_for
        return url_for('/scripts/third-party/flowplayer-3.1.5.swf', qualified=self.qualified)

    def flashvars(self):
        playlist = []
        vars = {
            'canvas': {'backgroundColor': '#000', 'backgroundGradient': 'none'},
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
    providers = {
        AUDIO: 'sound',
        VIDEO: 'video',
    }

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

        vars = {
            'image': thumb_url(self.media, 'l', qualified=self.qualified),
            'autostart': self.autoplay,
        }

        if self.file.container == 'youtube':
            vars['provider'] = 'youtube'
            vars['file'] = self.file.link_url(qualified=self.qualified)
        else:
            vars['provider'] = self.providers[self.file.type]
            vars['file'] = self.file.play_url(qualified=self.qualified)

        plugins = []
        audio_desc = self.media.audio_desc
        captions = self.media.captions
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

    def swf_url(self):
        return self.file.play_url(qualified=self.qualified)

    def flashvars(self):
        return {}

class HTML5Player(Player):
    """HTML5 <audio> / <video> tag.

    References:

        http://dev.w3.org/html5/spec/Overview.html#audio
        http://dev.w3.org/html5/spec/Overview.html#video
        http://developer.apple.com/safari/library/documentation/AudioVideo/Conceptual/Using_HTML5_Audio_Video/Introduction/Introduction.html

    """
    is_html5 = True

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
    """HTML5-based JWPlayer"""

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

players = {
    'flowplayer': FlowPlayer,
    'jwplayer': JWPlayer,
    'jwplayer-html5': JWPlayerHTML5,
    'youtube': EmbedPlayer,
    'google': EmbedPlayer,
    'vimeo': EmbedPlayer,
    'html5': HTML5Player,
    'sublime': HTML5Player,
}
"""Maps player names to classes that describe their behaviour.

The names are from the html5_player and flash_player settings.

You can use set 'youtube' to JWPlayer to take advantage of YouTube's
chromeless player. The only catch is that it doesn't support HD.
"""

player_controls_heights = {
    'youtube': 25,
    'google': 27,
    'flowplayer': 24,
    'jwplayer': 24,
    'jwplayer-html5': 0,
}
"""The height of the controls for each player.

We increase the height of the player by this number of pixels to
maintain a 16:9 aspect ratio.
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
        player_type=None, include_embedded=True):
    """Return the best choice of files to play and which player to use.

    XXX: This method uses the very unsophisticated technique of assuming
         that if the client is capable of playing the container format, then
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
    :returns: A :class:`~mediacore.model.media.MediaFile` object or None,
        a :class:`~mediacore.lib.helpers.Player` object or None,
        the detected browser name, and the detected browser version.
    :rtype: tuple

    """
    files = ordered_playable_files(media.files)

    # Only proceed if this file is a playable type.
    if not files:
        return None

    def get_html5_player():
        html5_supported_containers = [
            container
            for container, codecs
            in native_supported_types(browser, version)
        ]
        for file in files:
            if file.container in html5_supported_containers:
                return file, players[html5_player]
        return None, None

    def get_flash_player():
        if browser in flash_supported_browsers:
            for file in files:
                if file.container in flash_supported_containers:
                    return file, players[flash_player]
        return None, None

    def get_embedded_player():
        for file in files:
            if file.container in external_embedded_containers:
                return file, players[file.container]
        return None, None

    if browser is None:
        browser, version = parse_user_agent_version(user_agent)

    if player_type is None:
        player_type = app_globals.settings['player_type']

    html5_player = app_globals.settings['html5_player']
    flash_player = app_globals.settings['flash_player']

    file, player = None, None
    ef_file, ef_player = None, None
    eh_file, eh_player = None, None

    if player_type == 'html5':
        file, player = get_html5_player()

    elif player_type == 'best':
        # Prefer embedded videos with a HTML5 player
        # FIXME: Ignores client browser support for HTML5.
        if include_embedded:
            file, player = get_embedded_player()
            if player is not None and not player.is_html5:
                ef_file, ef_player = file, player
                file, player = None, None

        # Fall back to hosted videos with an HTML5 player
        if player is None:
            file, player = get_html5_player()

        # Fall back to embedded videos with a Flash player
        if player is None \
        and include_embedded \
        and browser in flash_supported_browsers:
            file, player = ef_file, ef_player

        # Fall back to hosted videos with a Flash player
        if player is None:
            file, player = get_flash_player()

        # Fall back to embedded videos with a Flash player, even if the
        # client browser doesn't support Flash. This ignorance is a last ditch
        # effort to allow devices to specially handle YouTube, Vimeo, et al.
        # e.g. It allows iPhones to display YouTube videos.
        if player is None and include_embedded:
            file, player = ef_file, ef_player

    elif player_type == 'flash':
        ef_file, ef_player = None, None

        # Prefer embedded videos with a Flash player
        if include_embedded:
            file, player = get_embedded_player()
            if player is not None:
                if player.is_flash and browser not in flash_supported_browsers:
                    ef_file, ef_player = file, player
                    file, player = None, None
                elif not player.is_flash:
                    eh_file, eh_player = file, player
                    file, player = None, None

        # Fall back to hosted videos with a Flash player
        if player is None:
            file, player = get_flash_player()

        # Fall back to embedded videos with an HTML5 player
        # FIXME: Ignores client browser support for HTML5.
        if player is None and include_embedded:
            file, player = eh_file, eh_player

        # Fall back to hosted videos with an HTML5 player
        if player is None:
            file, player = get_html5_player()

        # Fall back to embedded videos with a Flash player, even if the
        # client browser doesn't support Flash. This ignorance is a last ditch
        # effort to allow devices to specially handle YouTube, Vimeo, et al.
        # e.g. It allows iPhones to display YouTube videos.
        if player is None and include_embedded:
            file, player = ef_file, ef_player

    # Instantiate the player, and indicate whether to allow the player to
    # fail over to a different player inside the browser, if necessary.
    if player is not None:
        fallback = None
        if player_type != 'html5':
            if player.is_html5:
                fallback = players[flash_player]
            elif player.is_flash:
                fallback = players[html5_player]
        if fallback:
            fallback = fallback(media, file, browser=(browser, version))
        player = player(media, file, browser=(browser, version), fallback=fallback)

    return player
