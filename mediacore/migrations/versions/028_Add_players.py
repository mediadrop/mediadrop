# This file is a part of MediaDrop (http://www.mediadrop.net),
# Copyright 2009-2013 MediaCore Inc., Felix Schwarz and other contributors.
# For the exact contribution history, see the git revision log.
# The source code contained in this file is licensed under the GPLv3 or
# (at your option) any later version.
# See LICENSE.txt in the main project directory, for more information.

import logging
import simplejson
from datetime import datetime

from sqlalchemy import *
from sqlalchemy.types import MutableType, Text, TypeDecorator
from migrate import *

log = logging.getLogger(__name__)

class JsonType(MutableType, TypeDecorator):
    """
    JSON Type Decorator

    This converts JSON strings to python objects and vice-versa when
    working with SQLAlchemy Tables. The resulting python objects are
    mutable: SQLAlchemy will be aware of any changes you make within
    them, and they're saved automatically.

    """
    impl = Text

    def process_bind_param(self, value, dialect, dumps=simplejson.dumps):
        return dumps(value)

    def process_result_value(self, value, dialect, loads=simplejson.loads):
        return loads(value)

    def copy_value(self, value, loads=simplejson.loads, dumps=simplejson.dumps):
        return loads(dumps(value))

metadata = MetaData()

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

settings = Table('settings', metadata,
    Column('id', Integer, autoincrement=True, primary_key=True),
    Column('key', Unicode(255), nullable=False, unique=True),
    Column('value', UnicodeText),
    mysql_engine='InnoDB',
    mysql_charset='utf8',
)

DEFAULT_PLAYERS = [
    (u'youtube', True, {}),
    (u'vimeo', True, {}),
    (u'googlevideo', True, {}),
    (u'bliptv', True, {}),
    (u'html5', None, {}),
    (u'jwplayer', None, {}),
    (u'html5+jwplayer', None, {'prefer_flash': False}),
    (u'html5+flowplayer', None, {'prefer_flash': False}),
    (u'flowplayer', None, {}),
]

def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind migrate_engine
    # to your metadata
    metadata.bind = migrate_engine

    players.create()

    conn = migrate_engine.connect()
    transaction = conn.begin()

    # Grab the current player settings so we can setup the players table
    # to match the users preferences.
    settings_keys = settings.c.key.in_([
        u'player_type',
        u'flash_player',
        u'html5_player',
    ])
    settings_query = select([settings.c.key, settings.c.value]).where(settings_keys)
    settings_dict = dict(conn.execute(settings_query).fetchall())

    # Translate the old settings to a preferred player name.
    player_name = None
    # html5+jwplayer and html5+flowplayer both have this option which
    # replaces the old player_type setting.
    # prefer_flash = True means prefer flash over html5 whenever possible.
    prefer_flash = None

    if settings_dict['player_type'] == 'html5':
        player_name = u'html5'
    elif settings_dict['player_type'] in ('best', 'flash') \
    and settings_dict['flash_player'] in ('jwplayer', 'flowplayer'):
        player_name = u'html5+' + settings_dict['flash_player']
        prefer_flash = settings_dict['player_type'] == 'flash'
        log.info('PREFER_FLASH: %r', prefer_flash)
    else:
        player_name = u'html5+jwplayer'
        prefer_flash = False
        log.info('PREFER_FLASH: %r', prefer_flash)
    log.info('PREFER_FLASH: %r', prefer_flash)

    # Reorder our default players so that the preferred player comes first
    default_players = DEFAULT_PLAYERS[:]
    default_players.sort(key=lambda (name, enabled, data): name != player_name)

    for priority, (name, enabled, data) in enumerate(default_players):
        # Of our built in players, only the preferred one will be enabled
        if enabled is None:
            enabled = player_name == name
        # Set the prefer_flash argument if it applies for our preferred player
        if player_name == name \
        and prefer_flash is not None \
        and 'prefer_flash' in data:
            data['prefer_flash'] = prefer_flash
        conn.execute(players.insert().values(
            name=name,
            enabled=enabled,
            data=data,
            priority=priority,
        ))

    transaction.commit()
    conn.execute(settings.delete().where(settings_keys))

def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    metadata.bind = migrate_engine
    players.drop()
