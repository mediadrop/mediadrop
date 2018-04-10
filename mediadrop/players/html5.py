# -*- coding: utf-8 -*-
# This file is a part of MediaDrop (https://www.mediadrop.video),
# Copyright 2009-2018 MediaDrop contributors
# For the exact contribution history, see the git revision log.
# The source code contained in this file is licensed under the GPLv3 or
# (at your option) any later version.
# See LICENSE.txt in the main project directory, for more information.

from mediadrop.lib.i18n import N_
from .base_classes import AbstractHTML5Player


__all__ = ['HTML5Player']

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
