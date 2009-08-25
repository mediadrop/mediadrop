"""The application's model objects"""

import re
from zope.sqlalchemy import ZopeTransactionExtension
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from tg.exceptions import HTTPNotFound
from sqlalchemy.orm.exc import NoResultFound
from mediaplex.lib.unidecode import unidecode
from mediaplex.lib.htmlsanitizer import entities_to_unicode

# Global session manager.  DBSession() returns the session object
# appropriate for the current web request.
maker = sessionmaker(autoflush=True, autocommit=False,
                     extension=ZopeTransactionExtension())
DBSession = scoped_session(maker)

# By default, the data model is defined with SQLAlchemy's declarative
# extension, but if you need more control, you can switch to the traditional method.
DeclarativeBase = declarative_base()
# Global metadata. The default metadata is the one from the declarative base.
metadata = DeclarativeBase.metadata

# maximum length of slug strings for all objects.
slug_length = 50

#####
# Generally you will not want to define your table's mappers, and data objects
# here in __init__ but will want to create modules them in the model directory
# and import them at the bottom of this file.
######

def init_model(engine):
    """Call me before using any of the tables or classes in the model."""
    DBSession.configure(bind=engine)


def fetch_row(mapped_class, id=None, slug=None, incl_trash=False, extra_filter=None):
    """Fetch a row from the database which matches the ID, slug, and other filters.
    If the id arg is 'new', an new, empty instance is created.

    Raises a HTTPNotFound exception if no result is found.
    """
    if id == 'new':
        inst = mapped_class()
        return inst
    query = DBSession.query(mapped_class)
    if id is not None:
        query = query.filter_by(id=id)
    if slug is not None:
        query = query.filter_by(slug=slug)
    if extra_filter is not None:
        query = query.filter(extra_filter)
    if not incl_trash and hasattr(mapped_class, 'status'):
        query = query.filter(mapped_class.status.excludes('trash'))

    try:
        return query.one()
    except NoResultFound:
        raise HTTPNotFound

def slugify(string):
    """Transform a unicode string, potentially including XHTML entities
    into a viable slug string (ascii)"""
    # FIXME: these regular expressions don't ever change. We should perhaps
    #        create application-wide re.compile()'d regexes to do this.
    string = unicode(string).lower()
    # replace xhtml entities
    string = entities_to_unicode(string)
    # Transliterate to ASCII, as best as possible:
    string = unidecode(string)
    # String may now contain '[?]' triplets to describe unknown characters.
    # These will be stripped out by the following regexes.
    string = re.sub(r'\s+', u'-', string)
    string = re.sub(r'[^a-z0-9_-]', u'', string)
    string = re.sub(r'-+', u'-', string).strip('-')

    return string[:slug_length]

def get_available_slug(mapped_class, slug, ignore=None):
    """Return a unique slug based on the provided slug.

    Works by appending an int in sequence.

    mapped_class
      The ORM-controlled model that the slug is for

    slug
      The already slugified slug

    ignore
      An ID or instance of mapped_class which doesn't count as a collision
    """
    if isinstance(ignore, mapped_class):
        ignore = ignore.id
    elif ignore is not None:
        ignore = int(ignore)

    # ensure that the slug string is a valid slug
    slug = slugify(slug)

    # ensure the slug is unique by appending an int in sequence
    new_slug = slug
    appendix = 2
    while DBSession.query(mapped_class.id)\
            .filter(mapped_class.slug == new_slug)\
            .filter(mapped_class.id != ignore)\
            .first():

        str_appendix = '-' + str(appendix)
        max_substr_len = slug_length - len(str_appendix)
        new_slug = slug[:max_substr_len] + str_appendix
        appendix += 1

    return new_slug


from mediaplex.model.auth import User, Group, Permission
from mediaplex.model.authors import Author, AuthorWithIP
from mediaplex.model.rating import Rating
from mediaplex.model.comments import Comment
from mediaplex.model.tags import Tag
from mediaplex.model.topics import Topic
from mediaplex.model.media import Media, MediaFile
from mediaplex.model.podcasts import Podcast
