from webhelpers import paginate as _paginate
from webhelpers.paginate import get_wrapper

"""Adds Page.items_first_page """

class Page(_paginate.Page):
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
        #print 'itemsfirstpage', self.items_first_page

        # Unless the user tells us how many items the collections has
        # we calculate that ourselves.
        if item_count is not None:
            self.item_count = item_count
        else:
            self.item_count = len(self.collection)

        # Compute the number of the first and last available page
        if self.item_count > 0:
            self.first_page = 1
#            self.page_count = ((self.item_count - 1) / self.items_per_page) + 1
#            self.last_page = self.first_page + self.page_count - 1

            if self.items_first_page is None: # Go ahead with the default behaviour
                self.page_count = ((self.item_count - 1) / self.items_per_page) + 1
            else:
                other_items = self.item_count - self.items_first_page
                #print '# other items:', other_items
                if other_items <= 0:
                    self.page_count = 1
                else:
                    self.page_count = ((other_items - 1) / self.items_per_page) + 1 + 1
                    #print 'page count', self.page_count
            self.last_page = self.first_page + self.page_count - 1
            #print 'last page', self.last_page

            # Make sure that the requested page number is the range of valid pages
            if self.page > self.last_page:
                self.page = self.last_page
            elif self.page < self.first_page:
                self.page = self.first_page

            # Note: the number of items on this page can be less than
            #       items_per_page if the last page is not full
            if self.items_first_page is None: # Go ahead with the default behaviour again
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

