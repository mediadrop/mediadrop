import simplejson
from datetime import datetime

from sqlalchemy import *
from sqlalchemy.types import MutableType, Text, TypeDecorator
from migrate import *

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
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('type', Unicode(30), nullable=False),
    Column('display_name', Unicode(100), nullable=False, unique=True),
    Column('enabled', Boolean, nullable=False, default=True),
    Column('priority', Integer, nullable=False, default=0),
    Column('created_on', DateTime, nullable=False, default=datetime.now),
    Column('modified_on', DateTime, nullable=False, default=datetime.now,
                                                    onupdate=datetime.now),
    Column('data', JsonType, nullable=False, default=dict),
    mysql_engine='InnoDB',
    mysql_charset='utf8',
)

DEFAULT_PLAYERS = [
    (u'html5', 'Plain HTML5 Player', {}),
    (u'flowplayer', 'Flowplayer', {}),
    (u'jwplayer', 'JWPlayer', {}),
    (u'bliptv', 'BlipTV', {}),
    (u'googlevideo', 'Google Video', {}),
    (u'vimeo', 'Vimeo', {}),
    (u'youtube', 'YouTube', {}),
]

def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind migrate_engine
    # to your metadata
    metadata.bind = migrate_engine
    players.create()

def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    metadata.bind = migrate_engine
    players.drop()
