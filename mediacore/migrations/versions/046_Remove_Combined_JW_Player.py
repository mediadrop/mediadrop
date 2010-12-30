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
    query = players.delete().where(players.c.name==name)
    migrate_engine.execute(query)

def downgrade(migrate_engine):
    metadata.bind = migrate_engine
    count_query = players.select()
    all_players = migrate_engine.execute(count_query).fetchall()
    next_priority = len(all_players) + 1

    add_query = players.insert().values(
            name=name, data=data, priority=next_priority)
    migrate_engine.execute(add_query)
