"""
Podcast Models

Dependent on the Media module.

"""
from datetime import datetime
from sqlalchemy import Table, ForeignKey, Column
from sqlalchemy.types import String, Unicode, UnicodeText, Integer, DateTime, Boolean, Float
from sqlalchemy.orm import mapper, relation, backref, synonym, composite

from mediaplex.model import DeclarativeBase, metadata, DBSession
from mediaplex.model.authors import Author
from mediaplex.model.tags import Tag
from mediaplex.model.media import Media


podcasts = Table('podcasts', metadata,
    Column('id', Integer, autoincrement=True, primary_key=True),
    Column('slug', String(50), unique=True, nullable=False),
    Column('created_on', DateTime, default=datetime.now, nullable=False),
    Column('modified_on', DateTime, default=datetime.now, onupdate=datetime.now, nullable=False),
    Column('title', Unicode(50), nullable=False),
    Column('subtitle', Unicode(255)),
    Column('description', UnicodeText),
    Column('category', Unicode(50)),
    Column('author_name', Unicode(50)),
    Column('author_email', Unicode(50)),
    Column('copyright', Unicode(50)),
    Column('explicit', Boolean, default=False, nullable=False),
    Column('block_itunes', Boolean, default=False, nullable=False),
)

podcast_episodes = Table('podcast_episodes', metadata,
    Column('id', Integer, autoincrement=True, primary_key=True),
    Column('slug', String(50), nullable=False),
    Column('podcast_id', Integer, ForeignKey('podcasts.id', onupdate='CASCADE', ondelete='CASCADE'), nullable=False),
    Column('media_id', Integer, ForeignKey('media.id', onupdate='CASCADE', ondelete='CASCADE'), nullable=False),
    Column('created_on', DateTime, default=datetime.now, nullable=False),
    Column('modified_on', DateTime, default=datetime.now, onupdate=datetime.now, nullable=False),
    Column('publish_on', DateTime),
    Column('publish_until', DateTime),
    Column('title', Unicode(50), nullable=False),
    Column('subtitle', Unicode(255)),
    Column('description', UnicodeText),
    Column('category', Unicode(50)),
    Column('author_name', Unicode(50)),
    Column('author_email', Unicode(50)),
    Column('copyright', Unicode(50)),
)


class Podcast(object):
    """
    Podcast Model

    :param slug:
      Unique, search engine friendly ID

    :param created_on:
      DateTime created

    :param modified_on:
      DateTime last modified

    :param title:
      Full title

    :param subtitle:
      Short description

    :param description:
      Long summary

    :param category:
      Optional predefined iTunes categories listed at:
        http://www.apple.com/itunes/whatson/podcasts/specs.html#categories

    :param author:
      An instance of mediaplex.model.author.Author.

    :param copyright:
      Optional copyright to include in the feed

    :param explicit:
      Whether the podcast contains adult content

    :param block_itunes:
      Whether the podcast should be temporarily hidden from iTunes

    """
    def __repr__(self):
        return '<Podcast: %s>' % self.slug


class PodcastEpisode(object):
    """
    Podcast Episode Model

    :param slug:
      Unique, search engine friendly ID

    :param created_on:
      DateTime created

    :param modified_on:
      DateTime last modified

    :param publish_on:
      DateTime to publicly publish the episode in the feed

    :param invalid_on:
      DateTime to remove the episode from the public feed

    :param title:
      Full title

    :param subtitle:
      Short description

    :param description:
      Long summary

    :param category:
      Optional predefined iTunes categories listed at:
        http://www.apple.com/itunes/whatson/podcasts/specs.html#categories

    :param author:
      An instance of mediaplex.model.author.Author.

    :param copyright:
      Optional copyright to include in the feed

    """
    def __repr__(self):
        return '<PodcastEpisode: %s>' % self.slug


mapper(Podcast, podcasts, properties={
    'author': composite(Author, podcasts.c.author_name, podcasts.c.author_email),
    'episodes': relation(PodcastEpisode, backref='podcast'),
})
mapper(PodcastEpisode, podcast_episodes, properties={
    'author': composite(Author, podcast_episodes.c.author_name, podcast_episodes.c.author_email),
    'media': relation(Media, backref='episode'),
})
