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
from mediacore.model import DBSession, fetch_row, PlayerPrefs
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

        existing_db_names = set(p.name for p in players)
        existing_cls_names = set(p.name for p in AbstractPlayer)

        for name in existing_db_names.difference(existing_cls_names):
            for i, p in enumerate(players):
                if p.name == name:
                    break
            players.pop(i)

        for name in existing_cls_names.difference(existing_db_names):
            p = PlayerPrefs()
            p.name = name
            p.enabled = False
            players.append(p)

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

    @expose('json')
    def delete(self, id, **kwargs):
        """Delete a user.

        :param id: User ID.
        :type id: ``int``
        :returns: Redirect back to :meth:`index` after successful delete.
        """
