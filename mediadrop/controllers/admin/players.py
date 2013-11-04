# This file is a part of MediaDrop (http://www.mediadrop.net),
# Copyright 2009-2013 MediaDrop contributors
# For the exact contribution history, see the git revision log.
# The source code contained in this file is licensed under the GPLv3 or
# (at your option) any later version.
# See LICENSE.txt in the main project directory, for more information.

import logging

from pylons import tmpl_context
from webob.exc import HTTPException

from mediadrop.lib.auth import has_permission
from mediadrop.lib.base import BaseController
from mediadrop.lib.decorators import autocommit, expose, observable, validate
from mediadrop.lib.helpers import redirect, url_for
from mediadrop.lib.players import update_enabled_players
from mediadrop.model import (DBSession, PlayerPrefs, fetch_row,
    cleanup_players_table)
from mediadrop.plugin import events

log = logging.getLogger(__name__)

class PlayersController(BaseController):
    """Admin player preference actions"""
    allow_only = has_permission('admin')

    @expose('admin/players/index.html')
    @observable(events.Admin.PlayersController.index)
    def index(self, **kwargs):
        """List players.

        :rtype: Dict
        :returns:
            players
                The list of :class:`~mediadrop.model.players.PlayerPrefs`
                instances for this page.

        """
        players = PlayerPrefs.query.order_by(PlayerPrefs.priority).all()

        return {
            'players': players,
        }

    @expose('admin/players/edit.html')
    @observable(events.Admin.PlayersController.edit)
    def edit(self, id, name=None, **kwargs):
        """Display the :class:`~mediadrop.model.players.PlayerPrefs` for editing or adding.

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

    @expose(request_method='POST')
    @autocommit
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

    @expose(request_method='POST')
    @autocommit
    @observable(events.Admin.PlayersController.delete)
    def delete(self, id, **kwargs):
        """Delete a PlayerPref.

        After deleting the PlayerPref, cleans up the players table,
        ensuring that each Player class is represented--if the deleted
        PlayerPref is the last example of that Player class, creates a new
        disabled PlayerPref for that Player class with the default settings.

        :param id: Player ID.
        :type id: ``int``
        :returns: Redirect back to :meth:`index` after successful delete.
        """
        player = fetch_row(PlayerPrefs, id)
        DBSession.delete(player)
        DBSession.flush()
        cleanup_players_table()
        redirect(action='index', id=None)

    @expose(request_method='POST')
    @autocommit
    @observable(events.Admin.PlayersController.enable)
    def enable(self, id, **kwargs):
        """Enable a PlayerPref.

        :param id: Player ID.
        :type id: ``int``
        :returns: Redirect back to :meth:`index` after success.
        """
        player = fetch_row(PlayerPrefs, id)
        player.enabled = True
        update_enabled_players()
        redirect(action='index', id=None)

    @expose(request_method='POST')
    @autocommit
    @observable(events.Admin.PlayersController.disable)
    def disable(self, id, **kwargs):
        """Disable a PlayerPref.

        :param id: Player ID.
        :type id: ``int``
        :returns: Redirect back to :meth:`index` after success.
        """
        player = fetch_row(PlayerPrefs, id)
        player.enabled = False
        update_enabled_players()
        redirect(action='index', id=None)

    @expose(request_method='POST')
    @autocommit
    @observable(events.Admin.PlayersController.reorder)
    def reorder(self, id, direction, **kwargs):
        """Reorder a PlayerPref.

        :param id: Player ID.
        :type id: ``int``
        :param direction: ``"up"`` for higher priority, ``"down"`` for
            lower priority
        :type direction: ``unicode``
        :returns: Redirect back to :meth:`index` after success.
        """
        if direction == 'up':
            offset = -1
        elif direction == 'down':
            offset = 1
        else:
            return

        player1 = fetch_row(PlayerPrefs, id)
        new_priority = player1.priority + offset
        try:
            player2 = fetch_row(PlayerPrefs, priority=new_priority)
            player2.priority = player1.priority
            player1.priority = new_priority
        except HTTPException, e:
            if e.code != 404:
                raise

        redirect(action='index', id=None)
