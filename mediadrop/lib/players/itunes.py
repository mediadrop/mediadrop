# -*- coding: utf-8 -*-
# This file is a part of MediaDrop (https://www.mediadrop.video),
# Copyright 2009-2018 MediaDrop contributors
# For the exact contribution history, see the git revision log.
# The source code contained in this file is licensed under the GPLv3 or
# (at your option) any later version.
# See LICENSE.txt in the main project directory, for more information.

from mediadrop.lib.i18n import N_
from .base_classes import AbstractPlayer, FileSupportMixin, HTTP


__all__ = ['iTunesPlayer']

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
