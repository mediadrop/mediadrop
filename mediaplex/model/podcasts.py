from datetime import datetime
from sqlalchemy import Table, ForeignKey, Column
from sqlalchemy.types import String, Unicode, UnicodeText, Integer, DateTime, Boolean, Float
from sqlalchemy.orm import mapper, relation, backref, synonym, composite

from mediaplex.model import DeclarativeBase, metadata, DBSession
from mediaplex.model.author import Author
from mediaplex.model.rating import Rating
from mediaplex.model.comments import Comment, CommentTypeExtension
from mediaplex.model.tags import Tag
from mediaplex.model.media import Media


podcasts = Table('podcasts', metadata,
    Column('id', Integer, autoincrement=True, primary_key=True),
    Column('name', Unicode(50), nullable=False),
    Column('created_on', DateTime, default=datetime.now, nullable=False),
    Column('modified_on', DateTime, default=datetime.now, onupdate=datetime.now, nullable=False),
    Column('category', Unicode(50)),
    Column('explicit', Boolean, nullable=False),
    Column('subtitle', Unicode(255)),
    Column('summary', UnicodeText),
    Column('author', Unicode(50)),
    Column('copyright', Unicode(50)),
)

podcast_episodes = Table('podcast_episodes', metadata,
    Column('id', Integer, autoincrement=True, primary_key=True),
    Column('podcast_id', Integer, ForeignKey('podcasts.id', onupdate='CASCADE', ondelete='CASCADE')),
    Column('media_id', Integer, ForeignKey('media.id', onupdate='CASCADE', ondelete='CASCADE')),
    Column('created_on', DateTime, default=datetime.now, nullable=False),
    Column('modified_on', DateTime, default=datetime.now, onupdate=datetime.now, nullable=False),
    Column('publish_on', DateTime),
    Column('name', Unicode(50), nullable=False),
    Column('category', Unicode(50)),
    Column('subtitle', Unicode(255)),
    Column('summary', UnicodeText),
    Column('author', Unicode(50)),
    Column('copyright', Unicode(50)),
)


class Podcast(object):
    pass

class PodcastEpisode(object):
    pass


mapper(Podcast, podcasts, properties={
    'episodes': relation(PodcastEpisode, backref='podcast')
})
mapper(PodcastEpisode, podcast_episodes, properties={
    'media': relation(Media, backref='episode')
})
