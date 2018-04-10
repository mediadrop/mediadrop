# -*- coding: utf-8 -*-
# This file is a part of MediaDrop (https://www.mediadrop.video),
# Copyright 2009-2018 MediaDrop contributors
# For the exact contribution history, see the git revision log.
# The source code contained in this file is licensed under the GPLv3 or
# (at your option) any later version.
# See LICENSE.txt in the main project directory, for more information.

from genshi.core import Markup

from mediadrop.forms.admin import players as player_forms
from mediadrop.lib.filetypes import VIDEO
from mediadrop.lib.i18n import N_
from .base_classes import AbstractHTML5Player


__all__ = ['SublimePlayer']

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
