# This file is a part of MediaCore, Copyright 2010 Simple Station Inc.
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

import logging

from pylons import request, response, session, tmpl_context
from repoze.what.predicates import has_permission
from sqlalchemy import orm, sql

from mediacore.lib import helpers
from mediacore.lib.base import BaseController
from mediacore.lib.decorators import expose, observable, paginate, validate
from mediacore.lib.helpers import redirect, url_for
from mediacore.lib.players import AbstractPlayer
from mediacore.model import (DBSession, PlayerPrefs, fetch_row,
    cleanup_players_table)
from mediacore.plugin import events

log = logging.getLogger(__name__)

class PlayersController(BaseController):
    """Admin player preference actions"""
    allow_only = has_permission('admin')

    @expose('admin/players/index.html')
    def index(self, **kwargs):
        """List players.

        :rtype: Dict
        :returns:
            players
                The list of :class:`~mediacore.model.players.PlayerPrefs`
                instances for this page.

        """
        players = PlayerPrefs.query.all()

        return {
            'players': players,
        }

    @expose('admin/players/edit.html')
    def edit(self, id, name=None, **kwargs):
        """Display the :class:`~mediacore.model.players.PlayerPrefs` for editing or adding.

        :param id: PlayerPrefs ID
        :type id: ``int`` or ``"new"``
        :rtype: dict
        :returns:

        """
        playerp = fetch_row(PlayerPrefs, id)

        return {
            'player': playerp,
            'form': playerp.settings_form,
            'form_action': url_for(action='save'),
            'form_values': kwargs,
        }

    @expose()
    def save(self, id, **kwargs):
        player = fetch_row(PlayerPrefs, id)
        form = player.settings_form

        if id == 'new':
            DBSession.add(player)

        @validate(form, error_handler=self.edit)
        def save(id, **kwargs):
            # Allow the form to modify the player directly
            # since each can have radically different fields.
            save_func = getattr(form, 'save_data')
            save_func(player, **tmpl_context.form_values)
            redirect(controller='/admin/players', action='index')

        return save(id, **kwargs)

    @expose()
    def delete(self, id, **kwargs):
        """Delete a PlayerPref.

        After deleting the PlayerPref, cleans up the players table,
        ensuring that each Player class is represented
        If the deleted PlayerPref is the last example of that Player class,
        creates a new, 'disabled', PlayerPref for that Player class with
        the default settings.

        :param id: Player ID.
        :type id: ``int``
        :returns: Redirect back to :meth:`index` after successful delete.
        """
        player = fetch_row(PlayerPrefs, id)
        DBSession.delete(player)
        DBSession.flush()
        cleanup_players_table()
        redirect(action='index', id=None)

    @expose()
    def enable(self, id, **kwargs):
        """Enable a PlayerPref.

        :param id: Player ID.
        :type id: ``int``
        :returns: Redirect back to :meth:`index` after success.
        """
        player = fetch_row(PlayerPrefs, id)
        player.enabled = True
        redirect(action='index', id=None)

    @expose()
    def disable(self, id, **kwargs):
        """Disable a PlayerPref.

        :param id: Player ID.
        :type id: ``int``
        :returns: Redirect back to :meth:`index` after success.
        """
        player = fetch_row(PlayerPrefs, id)
        player.enabled = False
        redirect(action='index', id=None)
