# This file is a part of MediaCore, Copyright 2009 Simple Station Inc.
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
"""
Player Preferences

The :attr:`players` table defined here is used to persist the user's
preferences for, and the relative priority of, the different players
that MediaCore should try to play media with.

"""
import logging

from datetime import datetime

from sqlalchemy import Column, sql, Table
from sqlalchemy.orm import column_property, dynamic_loader, mapper
from sqlalchemy.orm.interfaces import MapperExtension
from sqlalchemy.types import Boolean, DateTime, Integer, Unicode

from mediacore.lib.decorators import memoize
from mediacore.lib.players import AbstractPlayer
from mediacore.model import JsonType
from mediacore.model.meta import DBSession, metadata

log = logging.getLogger(__name__)

players = Table('players', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True, doc=\
        """The primary key ID."""),

    Column('name', Unicode(30), nullable=False, doc=\
        """The internal name used to identify this player.

        Maps to :attr:`mediacore.lib.players.AbstractPlayer.name`.
        """),

    Column('enabled', Boolean, nullable=False, default=True, doc=\
        """A simple flag to disable the use of this player."""),

    Column('priority', Integer, nullable=False, default=0, doc=\
        """Order of preference in ascending order (0 is first)."""),

    Column('created_on', DateTime, nullable=False, default=datetime.now, doc=\
        """The date and time this player was first created."""),

    Column('modified_on', DateTime, nullable=False, default=datetime.now,
                                                    onupdate=datetime.now, doc=\
        """The date and time this player was last modified."""),

    Column('data', JsonType, nullable=False, default=dict, doc=\
        """The user preferences for this player (if any).

        This dictionary is passed as `data` kwarg when
        :func:`mediacore.lib.players.media_player` instantiates the
        :class:`mediacore.lib.players.AbstractPlayer` class associated
        with this row.

        """),

    mysql_engine='InnoDB',
    mysql_charset='utf8',
)

class PlayerPrefs(object):
    """
    Player Preferences

    A wrapper containing the administrator's preferences for an individual
    player. Each row maps to a :class:`mediacore.lib.players.AbstractPlayer`
    implementation.

    """
    query = DBSession.query_property()

    @property
    def player_cls(self):
        """Return the class object that is mapped to this row."""
        for player_cls in reversed(tuple(AbstractPlayer)):
            if self.name == player_cls.name:
                return player_cls
        return None

    @property
    def display_name(self):
        """Return the user-friendly display name for this player class.

        This string is expected to be i18n-ready. Simply wrap it in a
        call to :func:`pylons.i18n._`.

        :rtype: unicode
        :returns: A i18n-ready string name.
        """
        return self.player_cls.display_name

    @property
    @memoize
    def settings_form(self):
        cls = self.player_cls
        if cls and cls.settings_form_class:
            return cls.settings_form_class()
        return None

mapper(
    PlayerPrefs, players,
    order_by=(players.c.priority, players.c.id.desc()),
)

def fetch_enabled_players():
    """Return player classes and their data dicts in ascending priority.

    Warnings are logged any time a row is found that does not match up to
    one of the classes that are currently registered. A warning will also
    be raised if there are no players configured/enabled.

    :rtype: list of tuples
    :returns: :class:`~mediacore.lib.players.AbstractPlayer` subclasses
        and the configured data associated with them.

    """
    player_classes = dict((p.name, p) for p in AbstractPlayer)
    query = sql.select((players.c.name, players.c.data))\
        .where(players.c.enabled == True)\
        .order_by(players.c.priority.asc(), players.c.id.desc())
    query_data = DBSession.execute(query).fetchall()
    while query_data:
        try:
            return [(player_classes[name], data) for name, data in query_data]
        except KeyError:
            log.warn('Player name %r exists in the database but has not '
                     'been registered.' % name)
            query_data.remove((name, data))
    log.warn('No registered players are configured in your database.')
    return []
