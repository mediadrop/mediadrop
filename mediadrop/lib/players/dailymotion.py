# -*- coding: utf-8 -*-
# This file is a part of MediaDrop (https://www.mediadrop.video),
# Copyright 2009-2018 MediaDrop contributors
# For the exact contribution history, see the git revision log.
# The source code contained in this file is licensed under the GPLv3 or
# (at your option) any later version.
# See LICENSE.txt in the main project directory, for more information.

from urllib import urlencode

from genshi.builder import Element

from mediadrop.lib.i18n import N_
from .base_classes import AbstractIframeEmbedPlayer


__all__ = ['DailyMotionEmbedPlayer']

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

