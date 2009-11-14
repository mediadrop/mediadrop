"""The application's model objects"""

import re
from zope.sqlalchemy import ZopeTransactionExtension
from sqlalchemy.orm import scoped_session, sessionmaker, class_mapper
from sqlalchemy.ext.declarative import declarative_base
from tg.exceptions import HTTPNotFound
from sqlalchemy import sql, orm
from sqlalchemy.orm.exc import NoResultFound
from simpleplex.lib.unidecode import unidecode
from simpleplex.lib.htmlsanitizer import entities_to_unicode

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


def fetch_row(mapped_class, pk=None, incl_trash=False, extra_filter=None, **kwargs):
    """Fetch a single row from the database or else have TG display a 404.

    Typical usage is to fetch a single row for display or editing::

        class PageController(object):
            @expose()
            def index(self, id):
                page = fetch_row(Page, id)
                return page.name

            @expose()
            def works_with_slugs_too(self, slug):
                page = fetch_row(Page, slug=slug)
                return page.name

    If the ``pk`` is string ``new`` then an empty instance of ``mapped_class``
    is created and returned. This is helpful in admin controllers where you
    may reuse your *edit* action for *adding* too.

    :param mapped_class: An ORM-controlled model
    :param pk: A particular primary key to filter by.
    :type pk: int, ``None`` or ``"new"``
    :param incl_trash: By default we exclude rows with a status that includes
        ``trash``. Set this to true
    :type incl_trash: bool
    :param extra_filter: Extra filter arguments.
    :param \*\*kwargs: Any extra args are treated as column names to filter by.
        See :meth:`sqlalchemy.orm.Query.filter_by`.
    :returns: An instance of ``mapped_class``.
    :raises tg.exceptions.HTTPNotFound: If no result is found

    """
    if pk == 'new':
        inst = mapped_class()
        return inst

    query = DBSession.query(mapped_class)

    if pk is not None:
        mapper = class_mapper(mapped_class, compile=False)
        query = query.filter(mapper.primary_key[0] == pk)
    if kwargs:
        query = query.filter_by(**kwargs)
    if extra_filter is not None:
        query = query.filter(extra_filter)
    if not incl_trash and hasattr(mapped_class, 'status'):
        query = query.filter(mapped_class.status.excludes('trash'))

    try:
        return query.one()
    except NoResultFound:
        raise HTTPNotFound


# slugify regex's
_whitespace = re.compile(r'\s+')
_non_alpha = re.compile(r'[^a-z0-9_-]')
_extra_dashes = re.compile(r'-+')

def slugify(string):
    """Produce a URL-friendly string from the input.

    XHTML entities are converted to unicode, and then replaced with the
    best-choice ascii equivalents.

    :param string: A title, name, etc
    :type string: unicode
    :returns: Ascii URL-friendly slug
    :rtype: string

    """
    string = unicode(string).lower()
    # Replace xhtml entities
    string = entities_to_unicode(string)
    # Transliterate to ASCII, as best as possible:
    string = unidecode(string)
    # String may now contain '[?]' triplets to describe unknown characters.
    # These will be stripped out by the following regexes.
    string = _whitespace.sub(u'-', string)
    string = _non_alpha.sub(u'', string)
    string = _extra_dashes.sub(u'-', string).strip('-')

    return string[:slug_length]

def get_available_slug(mapped_class, string, ignore=None):
    """Return a unique slug based on the provided string.

    Works by appending an int in sequence starting with 2:

        1. awesome-stuff
        2. awesome-stuff-2
        3. awesome-stuff-3

    :param mapped_class: The ORM-controlled model that the slug is for
    :param string: A title, name, etc
    :type string: unicode
    :param ignore: A record which doesn't count as a collision
    :type ignore: Int ID, ``mapped_class`` instance or None
    :returns: A unique slug
    :rtype: string
    """
    if isinstance(ignore, mapped_class):
        ignore = ignore.id
    elif ignore is not None:
        ignore = int(ignore)

    new_slug = slug = slugify(string)
    appendix = 2
    while DBSession.query(mapped_class.id)\
            .filter(mapped_class.slug == new_slug)\
            .filter(mapped_class.id != ignore)\
            .first():
        str_appendix = '-%s' % appendix
        max_substr_len = slug_length - len(str_appendix)
        new_slug = slug[:max_substr_len] + str_appendix
        appendix += 1

    return new_slug

def _properties_dict_from_labels(*args):
    """Produce a dictionary of mapper properties from the given args list.

    Intended to make the process of producing lots of column properties
    less verbose and painful.

    """
    properties_dict = {}
    for property in args:
        label = property.columns[0].name
        properties_dict[label] = property
    return properties_dict

def _mtm_count_property(label, assoc_table,
                        where=None, deferred=True, **kwargs):
    """Return a column property for fetching the comment count for some object.

    :param label:
      A descriptive label for the correlated subquery. Should probably be the
      same as the name of the property set on the mapper.

    :param assoc_table:
      The many-to-many table which associates the comments table to the parent
      table. We expect the primary key to be two columns, one a foreign key to
      comments, the other a foreign key to the parent table.

    :param where:
      Optional additional where clauses. If given a list, the elements are
      wrapped in an AND clause.

    :param deferred:
      By default the count will be fetched when first accessed. To prefetch
      during the initial query, use:
        DBSession.query(ParentObject).options(undefer('comment_count_xyz'))
    :type deferred: bool

    :param \*\*kwargs:
      Any additional arguments are passed to sqlalchemy.orm.column_property
    """
    where_clauses = []
    for assoc_column in assoc_table.primary_key:
        fk = assoc_column.foreign_keys[0]
        where_clauses.append(fk.column == assoc_column)
    if isinstance(where, list):
        where_clauses.extend(where)
    elif where is not None:
        where_clauses.append(where)

    subselect = sql.select(
        [sql.func.coalesce(sql.func.count(sql.text('*')), sql.text('0'))],
        sql.and_(*where_clauses),
    )
    if label is not None:
        subselect = subselect.label(label)

    return orm.column_property(subselect, deferred=deferred, **kwargs)


from simpleplex.model.auth import User, Group, Permission
from simpleplex.model.authors import Author, AuthorWithIP
from simpleplex.model.rating import Rating
from simpleplex.model.comments import Comment
from simpleplex.model.settings import Setting
from simpleplex.model.tags import Tag
from simpleplex.model.topics import Topic
from simpleplex.model.media import Media, MediaFile
from simpleplex.model.podcasts import Podcast
