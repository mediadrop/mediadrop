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

from mediadrop.forms.admin import players as player_forms
from mediadrop.lib.i18n import N_
from mediadrop.lib.filetypes import AUDIO
from .base_classes import AbstractFlashPlayer, AbstractHTML5Player, HTTP
from .html5 import *
from mediadrop.lib.thumbnails import thumb_url
from mediadrop.lib.util import url_for


__all__ = ['FlowPlayer']

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
AbstractFlashPlayer.register(FlowPlayer)
