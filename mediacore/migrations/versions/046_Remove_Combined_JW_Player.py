# This file is a part of MediaDrop (http://www.mediadrop.net),
# Copyright 2009-2013 MediaCore Inc., Felix Schwarz and other contributors.
# For the exact contribution history, see the git revision log.
# The source code contained in this file is licensed under the GPLv3 or
# (at your option) any later version.
# See LICENSE.txt in the main project directory, for more information.

from sqlalchemy import *
from migrate import *
from datetime import datetime

metadata = MetaData()
players = Table('players', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('name', Unicode(30), nullable=False),
    Column('enabled', Boolean, nullable=False, default=False),
    Column('priority', Integer, nullable=False, default=0),
    Column('created_on', DateTime, nullable=False, default=datetime.now),
    Column('modified_on', DateTime, nullable=False, default=datetime.now, onupdate=datetime.now),
    Column('data', Text, nullable=False, default='{}'),
    mysql_engine='InnoDB',
    mysql_charset='utf8',
)

name = u'html5+jwplayer'
data = '{"prefer_flash": false}'

def upgrade(migrate_engine):
    metadata.bind = migrate_engine
    conn = migrate_engine.connect()

    # Before we delete the html5+jwplayer row, we want to ensure that the
    # standalone jwplayer will take the higher priority of the two.

    # Get the existing enabled/disabled and priority settings for both players
    query = select([players.c.name, players.c.enabled, players.c.priority])\
        .where(players.c.name.in_([u'jwplayer', u'html5+jwplayer']))

    # Create a dictionary where the enabled, most favored player (key)
    # evaluates to be *less than* the other.
    opts = dict((name, (not enabled, priority))
                for name, enabled, priority
                in conn.execute(query))

    # If html5+jwplayer is enabled and jwplayer is not or if they share an
    # enabled state and the html5+jwplayer is more preferred than jwplayer.
    if u'html5+jwplayer' in opts:
        if opts[u'html5+jwplayer'] < opts[u'jwplayer']:
            update_query = players.update()\
                .where(players.c.name == u'jwplayer')\
                .values(enabled=not opts[u'html5+jwplayer'][0], # un-negate above query
                        priority=opts[u'html5+jwplayer'][1])
            conn.execute(update_query)

        delete_query = players.delete().where(players.c.name == u'html5+jwplayer')
        conn.execute(delete_query)

def downgrade(migrate_engine):
    raise NotImplementedError()
