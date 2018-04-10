# -*- coding: utf-8 -*-
# This file is a part of MediaDrop (https://www.mediadrop.video),
# Copyright 2009-2018 MediaDrop contributors
# For the exact contribution history, see the git revision log.
# The source code contained in this file is licensed under the GPLv3 or
# (at your option) any later version.
# See LICENSE.txt in the main project directory, for more information.

from mediadrop.lib.i18n import N_
from .base_classes import AbstractFlashEmbedPlayer


__all__ = ['BlipTVFlashPlayer']

class BlipTVFlashPlayer(AbstractFlashEmbedPlayer):
    """
    BlipTV Player

    This simple player handles media with files that stored using
    :class:`mediadrop.lib.storage.BlipTVStorage`.

    """
    name = u'bliptv'
    """A unicode string identifier for this class."""

    display_name = N_(u'BlipTV')
    """A unicode display name for the class, to be used in the settings UI."""

    scheme = u'bliptv'
    """The `StorageURI.scheme` which uniquely identifies this embed type."""


AbstractFlashEmbedPlayer.register(BlipTVFlashPlayer)
