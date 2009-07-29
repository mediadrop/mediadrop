"""The application's model objects"""

from zope.sqlalchemy import ZopeTransactionExtension
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from tg.exceptions import HTTPNotFound
from sqlalchemy.orm.exc import NoResultFound

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

def get_available_slug(mapped_class, slug):
    """Return a unique slug based on the provided slug"""

    # ensure the slug is unique by appending an int in sequence
    slug_appendix = 2
    while DBSession.query(mapped_class.id)\
            .filter(mapped_class.slug == slug).first():

        str_appendix = str(slug_appendix)
        slug = slug[:-1-len(str_appendix)]
        slug += '-' + str_appendix
        slug_appendix += 1

    return slug


from mediaplex.model.auth import User, Group, Permission
from mediaplex.model.authors import Author, AuthorWithIP
from mediaplex.model.rating import Rating
from mediaplex.model.comments import Comment
from mediaplex.model.tags import Tag
from mediaplex.model.topics import Topic
from mediaplex.model.media import Media, PlaceholderMedia, Audio, Video, MediaFile
from mediaplex.model.podcasts import Podcast
