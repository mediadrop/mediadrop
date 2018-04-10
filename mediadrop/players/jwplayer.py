# -*- coding: utf-8 -*-
# This file is a part of MediaDrop (https://www.mediadrop.video),
# Copyright 2009-2018 MediaDrop contributors
# For the exact contribution history, see the git revision log.
# The source code contained in this file is licensed under the GPLv3 or
# (at your option) any later version.
# See LICENSE.txt in the main project directory, for more information.

from itertools import izip

from genshi.core import Markup
import simplejson

from mediadrop.lib.i18n import N_
from mediadrop.lib.filetypes import AUDIO, VIDEO, AUDIO_DESC, CAPTIONS
from mediadrop.lib.thumbnails import thumb_url
from mediadrop.lib.uri import pick_uris
from mediadrop.lib.util import url_for
from .base_classes import *


__all__ = ['JWPlayer']

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
