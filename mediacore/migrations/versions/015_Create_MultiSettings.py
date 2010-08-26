from sqlalchemy import *
from migrate import *
from migrate.changeset.schema import ChangesetColumn

metadata = MetaData()

multisettings = Table('settings_multi', metadata,
    Column('id', Integer, autoincrement=True, primary_key=True),
    Column('key', Unicode(255), nullable=False),
    Column('value', UnicodeText, nullable=False),
    mysql_engine='InnoDB',
    mysql_charset='utf8',
)

def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind migrate_engine
    # to your metadata
    metadata.bind = migrate_engine
    multisettings.create()

def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    metadata.bind = migrate_engine
    multisettings.drop()

