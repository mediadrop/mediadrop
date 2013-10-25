# This file is a part of MediaDrop (http://www.mediadrop.net),
# Copyright 2009-2013 MediaDrop contributors
# For the exact contribution history, see the git revision log.
# The source code contained in this file is licensed under the GPLv3 or
# (at your option) any later version.
# See LICENSE.txt in the main project directory, for more information.

import inspect
import warnings

from pylons import request, tmpl_context
from webhelpers.paginate import get_wrapper
from webob.multidict import MultiDict
from webhelpers.paginate import Page

from mediacore.lib.compat import wraps

# TODO: Move the paginate decorator to mediacore.lib.decorators,
#       and rework it to use the decorators module. This whole
#       module could be greatly simplified, and my CustomPage
#       class can be removed since it is no longer used as of
#       the v0.8.0 frontend redesign.

# FIXME: The following class is taken from TG2.0.3. Find a way to replace it.
# This is not an ideal solution, but avoids the immediate need to rewrite the
# paginate and CustomPage methods below.
# TG license: http://turbogears.org/2.0/docs/main/License.html
class Bunch(dict):
    """A dictionary that provides attribute-style access."""

    def __getitem__(self, key):
        return  dict.__getitem__(self, key)

    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            return get_partial_dict(name, self)

    __setattr__ = dict.__setitem__

    def __delattr__(self, name):
        try:
            del self[name]
        except KeyError:
            raise AttributeError(name)

# The following method is taken from TG2.0.3 (tg/util.py).
def get_partial_dict(prefix, dictionary):
    """Given a dictionary and a prefix, return a Bunch, with just items
    that start with prefix

    The returned dictionary will have 'prefix.' stripped so:

    get_partial_dict('prefix', {'prefix.xyz':1, 'prefix.zyx':2, 'xy':3})

    would return:

    {'xyz':1,'zyx':2}
    """

    match = prefix + "."

    new_dict = Bunch([(key.lstrip(match), dictionary[key])
                       for key in dictionary.iterkeys()
                       if key.startswith(match)])
    if new_dict:
        return new_dict
    else:
        raise AttributeError

# FIXME: The following function is taken from TG2.0.3. Find a way to replace it.
# This is not an ideal solution, but avoids the immediate need to rewrite the
# paginate and CustomPage methods below.
# TG license: http://turbogears.org/2.0/docs/main/License.html
def partial(*args, **create_time_kwds):
    func = args[0]
    create_time_args = args[1:]
    def curried_function(*call_time_args, **call_time_kwds):
        args = create_time_args + call_time_args
        kwds = create_time_kwds.copy()
        kwds.update(call_time_kwds)
        return func(*args, **kwds)
    return curried_function

def paginate(name, items_per_page=10, use_prefix=False, items_first_page=None):
    """Paginate a given collection.

    Duplicates and extends the functionality of :func:`tg.decorators.paginate` to:

        * Copy the docstring of the exposed method to the decorator, allowing
          :mod:`sphinx.ext.autodoc` to read docstring.
        * Support our :class:`CustomPage` extension -- used any time
          ``items_first_page`` is provided.

    This decorator is mainly exposing the functionality
    of :func:`webhelpers.paginate`.

    You use this decorator as follows::

     class MyController(object):

         @expose()
         @paginate("collection")
         def sample(self, *args):
             collection = get_a_collection()
             return dict(collection=collection)

    To render the actual pager, use::

      ${tmpl_context.paginators.<name>.pager()}

    where c is the tmpl_context.

    It is possible to have several :func:`paginate`-decorators for
    one controller action to paginate several collections independently
    from each other. If this is desired, don't forget to set the :attr:`use_prefix`-parameter
    to :const:`True`.

    :Parameters:
      name
        the collection to be paginated.
      items_per_page
        the number of items to be rendered. Defaults to 10
      use_prefix
        if True, the parameters the paginate
        decorator renders and reacts to are prefixed with
        "<name>_". This allows for multi-pagination.
      items_first_page
        the number of items to be rendered on the first page. Defaults to the
        value of ``items_per_page``

    """
    prefix = ""
    if use_prefix:
        prefix = name + "_"
    own_parameters = dict(
        page="%spage" % prefix,
        items_per_page="%sitems_per_page" % prefix
        )
    #@decorator
    def _d(f):
        @wraps(f)
        def _w(*args, **kwargs):
            page = int(kwargs.pop(own_parameters["page"], 1))
            real_items_per_page = int(
                    kwargs.pop(
                            own_parameters['items_per_page'],
                            items_per_page))

            # Iterate over all of the named arguments expected by the function f
            # if any of those arguments have values present in the kwargs dict,
            # add the value to the positional args list, and remove it from the
            # kwargs dict
            argvars = inspect.getargspec(f)[0][1:]
            if argvars:
                args = list(args)
                for i, var in enumerate(args):
                    if i>=len(argvars):
                        break;
                    var = argvars[i]
                    if var in kwargs:
                        if i+1 >= len(args):
                            args.append(kwargs[var])
                        else:
                            args[i+1] = kwargs[var]
                        del kwargs[var]

            res = f(*args, **kwargs)
            if isinstance(res, dict) and name in res:
                additional_parameters = MultiDict()
                for key, value in request.params.iteritems():
                    if key not in own_parameters:
                        additional_parameters.add(key, value)

                collection = res[name]

                # Use CustomPage if our extra custom arg was provided
                if items_first_page is not None:
                    page_class = CustomPage
                else:
                    page_class = Page

                page = page_class(
                    collection,
                    page,
                    items_per_page=real_items_per_page,
                    items_first_page=items_first_page,
                    **additional_parameters.dict_of_lists()
                    )
                # wrap the pager so that it will render
                # the proper page-parameter
                page.pager = partial(page.pager,
                        page_param=own_parameters["page"])
                res[name] = page
                # this is a bit strange - it appears
                # as if c returns an empty
                # string for everything it dosen't know.
                # I didn't find that documented, so I
                # just put this in here and hope it works.
                if not hasattr(tmpl_context, 'paginators') or type(tmpl_context.paginators) == str:
                    tmpl_context.paginators = Bunch()
                tmpl_context.paginators[name] = page
            return res
        return _w
    return _d


class CustomPage(Page):
    """A list/iterator of items representing one page in a larger
    collection.

    An instance of the "Page" class is created from a collection of things.
    The instance works as an iterator running from the first item to the
    last item on the given page. The collection can be:

    - a sequence
    - an SQLAlchemy query - e.g.: Session.query(MyModel)
    - an SQLAlchemy select - e.g.: sqlalchemy.select([my_table])

    A "Page" instance maintains pagination logic associated with each
    page, where it begins, what the first/last item on the page is, etc.
    The pager() method creates a link list allowing the user to go to
    other pages.

    **WARNING:** Unless you pass in an item_count, a count will be
    performed on the collection every time a Page instance is created.
    If using an ORM, it's advised to pass in the number of items in the
    collection if that number is known.

    Instance attributes:

    original_collection
        Points to the collection object being paged through

    item_count
        Number of items in the collection

    page
        Number of the current page

    items_per_page
        Maximal number of items displayed on a page

    first_page
        Number of the first page - starts with 1

    last_page
        Number of the last page

    page_count
        Number of pages

    items
        Sequence/iterator of items on the current page

    first_item
        Index of first item on the current page - starts with 1

    last_item
        Index of last item on the current page

    """
    def __init__(self, collection, page=1, items_per_page=20,
        items_first_page=None,
        item_count=None, sqlalchemy_session=None, *args, **kwargs):
        """Create a "Page" instance.

        Parameters:

        collection
            Sequence, SQLAlchemy select object or SQLAlchemy ORM-query
            representing the collection of items to page through.

        page
            The requested page number - starts with 1. Default: 1.

        items_per_page
            The maximal number of items to be displayed per page.
            Default: 20.

        item_count (optional)
            The total number of items in the collection - if known.
            If this parameter is not given then the paginator will count
            the number of elements in the collection every time a "Page"
            is created. Giving this parameter will speed up things.

        sqlalchemy_session (optional)
            If you want to use an SQLAlchemy (0.4) select object as a
            collection then you need to provide an SQLAlchemy session object.
            Select objects do not have a database connection attached so it
            would not be able to execute the SELECT query.

        Further keyword arguments are used as link arguments in the pager().
        """
        # 'page_nr' is deprecated.
        if 'page_nr' in kwargs:
            warnings.warn("'page_nr' is deprecated. Please use 'page' instead.")
            page = kwargs['page_nr']
            del kwargs['page_nr']

        # 'current_page' is also deprecated.
        if 'current_page' in kwargs:
            warnings.warn("'current_page' is deprecated. Please use 'page' instead.")
            page = kwargs['current_page']
            del kwargs['current_page']

        # Safe the kwargs class-wide so they can be used in the pager() method
        self.kwargs = kwargs

        # Save a reference to the collection
        self.original_collection = collection

        # Decorate the ORM/sequence object with __getitem__ and __len__
        # functions to be able to get slices.
        if collection:
            # Determine the type of collection and use a wrapper for ORMs
            self.collection = get_wrapper(collection, sqlalchemy_session)
        else:
            self.collection = []

        # The self.page is the number of the current page.
        # The first page has the number 1!
        try:
            self.page = int(page) # make it int() if we get it as a string
        except ValueError:
            self.page = 1

        self.items_per_page = items_per_page
        self.items_first_page = items_first_page # Adddddd

        # Unless the user tells us how many items the collections has
        # we calculate that ourselves.
        if item_count is not None:
            self.item_count = item_count
        else:
            self.item_count = len(self.collection)

        # Compute the number of the first and last available page
        if self.item_count > 0:
            self.first_page = 1

            if self.items_first_page is None:
                # Go ahead with the default behaviour
                self.page_count = \
                    ((self.item_count - 1) / self.items_per_page) + 1
            else:
                other_items = self.item_count - self.items_first_page
                if other_items <= 0:
                    self.page_count = 1
                else:
                    self.page_count = \
                        ((other_items - 1) / self.items_per_page) + 1 + 1
            self.last_page = self.first_page + self.page_count - 1

            # Make sure that the requested page number is the range of valid pages
            if self.page > self.last_page:
                self.page = self.last_page
            elif self.page < self.first_page:
                self.page = self.first_page

            # Note: the number of items on this page can be less than
            #       items_per_page if the last page is not full
            if self.items_first_page is None:
                # Go ahead with the default behaviour again
                self.first_item = (self.page - 1) * items_per_page + 1
                self.last_item = min(self.first_item + items_per_page - 1, self.item_count)
            else:
                if self.page == 1:
                    self.first_item = 1
                    self.last_item = min(self.items_first_page, self.item_count)
                else:
                    self.first_item = (self.page - 2) * items_per_page + 1 + self.items_first_page
                    self.last_item = min(self.first_item + items_per_page - 1, self.item_count)

            # We subclassed "list" so we need to call its init() method
            # and fill the new list with the items to be displayed on the page.
            # We use list() so that the items on the current page are retrieved
            # only once. Otherwise it would run the actual SQL query everytime
            # .items would be accessed.
            self.items = list(self.collection[self.first_item-1:self.last_item])

            # Links to previous and next page
            if self.page > self.first_page:
                self.previous_page = self.page-1
            else:
                self.previous_page = None

            if self.page < self.last_page:
                self.next_page = self.page+1
            else:
                self.next_page = None

        # No items available
        else:
            self.first_page = None
            self.page_count = 0
            self.last_page = None
            self.first_item = None
            self.last_item = None
            self.previous_page = None
            self.next_page = None
            self.items = []

        # This is a subclass of the 'list' type. Initialise the list now.
        list.__init__(self, self.items)

