# This file is a part of MediaDrop (http://www.mediadrop.net),
# Copyright 2009-2013 MediaDrop contributors
# For the exact contribution history, see the git revision log.
# The source code contained in this file is licensed under the GPLv3 or
# (at your option) any later version.
# See LICENSE.txt in the main project directory, for more information.
"""
Player Preferences

The :attr:`players` table defined here is used to persist the user's
preferences for, and the relative priority of, the different players
that MediaDrop should try to play media with.

"""

import logging
from datetime import datetime

from sqlalchemy import Column, sql, Table
from sqlalchemy.orm import mapper
from sqlalchemy.types import Boolean, DateTime, Integer, Unicode

from mediadrop.lib.decorators import memoize
from mediadrop.lib.i18n import _
from mediadrop.lib.players import AbstractPlayer
from mediadrop.model.meta import DBSession, metadata
from mediadrop.model.util import JSONType

log = logging.getLogger(__name__)

players = Table('players', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True, doc=\
        """The primary key ID."""),

    Column('name', Unicode(30), nullable=False, doc=\
        """The internal name used to identify this player.

        Maps to :attr:`mediadrop.lib.players.AbstractPlayer.name`.
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

    Column('data', JSONType, nullable=False, default=dict, doc=\
        """The user preferences for this player (if any).

        This dictionary is passed as `data` kwarg when
        :func:`mediadrop.lib.players.media_player` instantiates the
        :class:`mediadrop.lib.players.AbstractPlayer` class associated
        with this row.

        """),

    mysql_engine='InnoDB',
    mysql_charset='utf8',
)

class PlayerPrefs(object):
    """
    Player Preferences

    A wrapper containing the administrator's preferences for an individual
    player. Each row maps to a :class:`mediadrop.lib.players.AbstractPlayer`
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
        call to :func:`mediadrop.lib.i18n._`.

        :rtype: unicode
        :returns: A i18n-ready string name.
        """
        if self.player_cls is None:
            # do not break the admin interface (admin/settings/players) if the
            # player is still in the database but the actual player class is not
            # available anymore (this can happen especially for players provided
            # by external plugins.
            return _(u'%s (broken)') % self.name
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
    order_by=(
        players.c.enabled.desc(),
        players.c.priority,
        players.c.id.desc(),
    ),
)

def fetch_enabled_players():
    """Return player classes and their data dicts in ascending priority.

    Warnings are logged any time a row is found that does not match up to
    one of the classes that are currently registered. A warning will also
    be raised if there are no players configured/enabled.

    :rtype: list of tuples
    :returns: :class:`~mediadrop.lib.players.AbstractPlayer` subclasses
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

def cleanup_players_table(enabled=False):
    """
    Ensure that all available players are added to the database
    and that players are prioritized in incrementally increasing order.

    :param enabled: Should the default players be enabled upon creation?
    :type enabled: bool
    """
    from mediadrop.lib.players import (BlipTVFlashPlayer,
        DailyMotionEmbedPlayer, GoogleVideoFlashPlayer, JWPlayer,
        VimeoUniversalEmbedPlayer, YoutubePlayer)

    # When adding players, prefer them in the following order:
    default_players = [
        JWPlayer,
        YoutubePlayer,
        VimeoUniversalEmbedPlayer,
        GoogleVideoFlashPlayer,
        BlipTVFlashPlayer,
        DailyMotionEmbedPlayer,
    ]
    unordered_players = [p for p in AbstractPlayer if p not in default_players]
    all_players = default_players + unordered_players

    # fetch the players that are already in the database
    s = players.select().order_by('priority')
    existing_players_query = DBSession.execute(s)
    existing_player_rows = [p for p in existing_players_query]
    existing_player_names = [p['name'] for p in existing_player_rows]

    # Ensure all priorities are monotonically increasing from 1..n
    priority = 0
    for player_row in existing_player_rows:
        priority += 1
        if player_row['priority'] != priority:
            u = players.update()\
                       .where(players.c.id == player_row['id'])\
                       .values(priority=priority)
            DBSession.execute(u)

    # Ensure that all available players are in the database
    for player_cls in all_players:
        if player_cls.name not in existing_player_names:
            enable_player = enabled and player_cls in default_players
            priority += 1
            DBSession.execute(players.insert().values(
                name=player_cls.name,
                enabled=enable_player,
                data=player_cls.default_data,
                priority=priority,
            ))
