# -*- coding: utf-8 -*-
# This file is a part of MediaDrop (https://www.mediadrop.video),
# Copyright 2009-2018 MediaDrop contributors
# For the exact contribution history, see the git revision log.
# The source code contained in this file is licensed under the GPLv3 or
# (at your option) any later version.
# See LICENSE.txt in the main project directory, for more information.

from urllib import urlencode

from genshi.builder import Element

from mediadrop.forms.admin import players as player_forms
from mediadrop.lib.i18n import N_
from .base_classes import AbstractIframeEmbedPlayer


__all__ = ['YoutubePlayer']

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
