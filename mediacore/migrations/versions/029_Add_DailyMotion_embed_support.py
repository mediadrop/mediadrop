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

storage = Table('storage', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('engine_type', Unicode(30), nullable=False),
    Column('display_name', Unicode(100), nullable=False, unique=True),
    Column('enabled', Boolean, nullable=False, default=True),
    Column('created_on', DateTime, nullable=False, default=datetime.now),
    Column('modified_on', DateTime, nullable=False, default=datetime.now,
                                                    onupdate=datetime.now),
    Column('data', JsonType, nullable=False, default=dict),
    mysql_engine='InnoDB',
    mysql_charset='utf8',
)

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

def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind migrate_engine
    # to your metadata
    metadata.bind = migrate_engine

    conn = migrate_engine.connect()
    transaction = conn.begin()

    max_priority_query = select([func.max(players.c.priority)])
    max_priority = conn.execute(max_priority_query).scalar()

    conn.execute(players.insert().values(
        name=u'dailymotion',
        enabled=1,
        data={},
        priority=max_priority + 1,
    ))

    conn.execute(storage.insert().values(
        engine_type=u'DailyMotionStorage',
        display_name=u'Daily Motion',
        enabled=1,
        data={},
    ))

    transaction.commit()

def downgrade(migrate_engine):
    raise NotImplementedError()
