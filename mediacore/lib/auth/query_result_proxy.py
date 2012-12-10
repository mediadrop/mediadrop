# -*- coding: utf-8 -*-
# This file is a part of MediaCore CE, Copyright 2009-2012 MediaCore Inc.
# The source code in this file is dual licensed under the MIT license or the 
# GPL version 3 or (at your option) any later version.
# See LICENSE.txt in the main project directory, for more information.
#
# Copyright (c) 2012 Felix Schwarz <felix.schwarz@oss.schwarz.eu>


__all__ = ['QueryResultProxy']

class QueryResultProxy(object):
    def __init__(self, query, start=0, filter_=None, default_fetch=10):
        self.query = query
        self._items_retrieved = start
        self._items_returned = 0
        self._limit = None
        self._filter = filter_
        self._default_fetch = default_fetch
        self._prefetched_items = []
    
    def fetch(self, n=1):
        assert n >= 1
        if self._limit is not None:
            if self._items_returned + n > self._limit:
                n = self._limit - self._items_returned
                if n < 1:
                    return []
        new_items = []
        if len(self._prefetched_items) > 0:
            new_items.extend(self._prefetched_items[:n])
            self._prefetched_items = self._prefetched_items[n:]
        # don't adapt number of items to fetch during the loops - otherwise we
        # might have to do a lot of queries to get the last missing items in a
        # situation where only few items from a big list are acceptable to the
        # filter
        n_ = n - len(new_items)
        while len(new_items) < n:
            number_of_items_to_fetch = max(n_+1, self._default_fetch)
            fetched_items = self._fetch(number_of_items_to_fetch)
            retrieved_items = filter(self._filter, fetched_items)
            new_items.extend(retrieved_items)
            if len(fetched_items) <= n_:
                # if there were only "n_" items left (though we requested 'n_+1'
                # we're done, we consumed all available items.
                break
        self._prefetched_items.extend(new_items[n:])
        
        items = new_items[:n]
        self._items_returned += len(items)
        return items
    
    def _fetch(self, n):
        fetched_items = self.query.offset(self._items_retrieved).limit(n).all()
        self._items_retrieved += len(fetched_items)
        return fetched_items
    
    def more_available(self):
        if len(self._prefetched_items) == 0:
            next_items = self.fetch(n=1)
            if len(next_items) > 0:
                # fetch will increase the number if items returned but we won't
                # return the actual item here.
                self._items_returned -= len(next_items)
                self._prefetched_items.insert(0, next_items[0])
        return len(self._prefetched_items) > 0
    
    def first(self):
        "Returns the next available item or None if there are no items anymore."
        item = self.fetch(1)
        if len(item) == 0:
            return None
        return item[0]
    
    # --- pagination support ---------------------------------------------------
    
    def __iter__(self):
        return self
    
    def next(self):
        items = self.fetch(n=1)
        if len(items) > 0:
            return items[0]
        raise StopIteration
    
    def _prefetch_all(self):
        # yes, that's very inefficient but works for now
        prefetched_items = []
        def _prefetch():
            next_items = self.fetch(n=1000)
            self._items_returned -= len(next_items)
            prefetched_items.extend(next_items)
            prefetched_items.extend(self._prefetched_items)
            self._prefetched_items = []
            return (len(next_items) == 1000)
        while _prefetch():
            pass
        self._prefetched_items = prefetched_items
    
    def __len__(self):
        if self.more_available():
            self._prefetch_all()
        return self._items_returned + len(self._prefetched_items)
    count = __len__
    
    def __getitem__(self, key):
        def is_slice(item):
            return hasattr(key, 'indices')
        
        if is_slice(key):
            start, stop, step = key.indices(len(self))
            # TODO: if start < self._items_returned
            index_start = start - self._items_returned
            index_stop = index_start + (stop - start)
            
            # TODO: support step
            return self._prefetched_items[index_start:index_stop]
        raise TypeError
    
    def limit(self, n):
        n = int(n)
        assert n >= 1
        self._limit = n
        return self
    
    def offset(self, n):
        n = int(n)
        assert n >= 0
        assert self._items_retrieved == 0
        assert self._items_returned == 0
        self._items_retrieved = n
        return self


