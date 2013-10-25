# -*- coding: utf-8 -*-
# This file is a part of MediaDrop (http://www.mediadrop.net),
# Copyright 2009-2013 MediaDrop contributors
# For the exact contribution history, see the git revision log.
# The source code in this file is is dual licensed under the MIT license or
# the GPLv3 or (at your option) any later version.
# See LICENSE.txt in the main project directory, for more information.

from sqlalchemy import Column, Integer, String
from sqlalchemy import asc, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from mediacore.lib.auth.query_result_proxy import QueryResultProxy
from mediacore.lib.test.pythonic_testcase import *


Base = declarative_base()
class User(Base):
    __tablename__ = 'test_queryresultproxy_users'
    
    id = Column(Integer, primary_key=True)
    name = Column(String)
    activity = Column(Integer)
    
    def __init__(self, name, activity):
        self.name = name
        self.activity = activity
    
    def __repr__(self):
        return 'User(name=%s, activity=%s)' % (repr(self.name), repr(self.activity))



class QueryResultProxyTest(PythonicTestCase):
    def setUp(self):
        self.engine = create_engine('sqlite:///:memory:')
        self.session = self._create_session()
        self._populate_database()
        self.query = self.session.query(User).order_by(asc(User.id))
        self.proxy = QueryResultProxy(self.query)
    
    def _tearDown(self):
        Base.metadata.drop_all(self.engine)
    
    def _create_session(self):
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        return Session()
    
    def _populate_database(self):
        for i, name in enumerate(('foo', 'bar', 'baz', 'quux', 'quuux')):
            self.session.add(User(name, i))
        self.session.commit()
    
    def _next_name(self):
        items = self.proxy.fetch(n=1)
        return items[0].name
    
    def _next_names(self, n=1):
        return self._names(self.proxy.fetch(n=n))
    
    def _names(self, results):
        return [item.name for item in results]
    
    def _name(self, result):
        return result.name
    
    def test_can_fetch_next_item(self):
        assert_equals('foo', self._next_name())
        assert_equals('bar', self._next_name())
        assert_equals('baz', self._next_name())
    
    def test_can_fetch_single_item(self):
        filter_ = lambda item: item.activity >= 4
        self.proxy = QueryResultProxy(self.query, filter_=filter_)
        assert_equals('quuux', self._name(self.proxy.first()))
        assert_equals(None, self.proxy.first())
    
    def test_can_fetch_multiple_items_at_once(self):
        assert_equals(['foo', 'bar'], self._next_names(n=2))
        assert_equals(['baz', 'quux'], self._next_names(n=2))
        assert_equals(['quuux'], self._next_names(n=2))
        assert_equals([], self._next_names(n=2))
    
    def test_regression_do_not_skipped_items_because_of_prefetching(self):
        assert_equals('foo', self._next_name())
        assert_equals(['bar', 'baz'], self._next_names(n=2))
        assert_equals(['quux', 'quuux'], self._next_names(n=2))
    
    def test_can_tell_if_more_items_are_available_even_before_explicit_fetching(self):
        assert_true(self.proxy.more_available())
        assert_equals('foo', self._next_name())
    
    def test_can_tell_if_no_more_items_are_available(self):
        assert_equals(['foo', 'bar', 'baz', 'quux'], self._next_names(n=4))
        assert_true(self.proxy.more_available())
        
        assert_equals('quuux', self._next_name())
        assert_false(self.proxy.more_available())
    
    def test_does_not_omit_prefetched_items_after_asking_if_more_are_available(self):
        assert_true(self.proxy.more_available())
        assert_equals(['foo', 'bar'], self._next_names(n=2))
    
    def test_does_not_omit_prefetched_items_if_many_prefetched_items_were_available(self):
        assert_true(self.proxy.more_available())
        # more_available() should have fetched more than one item so we have 
        # actually 2+ items prefetched.
        assert_not_equals(0, len(self.proxy._prefetched_items))
        # .next() consumes only one item so there should be one left
        # (._prefetched_items were overwritten in this step)
        assert_equals(['foo'], self._names([self.proxy.next()]))
        assert_not_equals(0, len(self.proxy._prefetched_items))
        
        assert_equals(['bar', 'baz'], self._next_names(n=2))
    
    def test_can_initialize_proxy_with_offset(self):
        self.proxy = QueryResultProxy(self.query, start=2)
        assert_equals(['baz', 'quux'], self._next_names(n=2))
    
    def test_can_specify_filter_callable(self):
        filter_ = lambda item: item.activity % 2 == 1
        self.proxy = QueryResultProxy(self.query, filter_=filter_)
        assert_equals(['bar', 'quux'], self._next_names(n=5))
        assert_false(self.proxy.more_available())
    
    def test_proxy_returns_always_specified_number_of_items_if_possible(self):
        filter_ = lambda item: item.activity >= 2
        self.proxy = QueryResultProxy(self.query, filter_=filter_)
        assert_equals(['baz', 'quux', 'quuux'], self._next_names(n=3))
        assert_false(self.proxy.more_available())
    
    # --- limit ----------------------------------------------------------------
    
    def test_can_limit_items_returned_by_iteration(self):
        self.proxy = QueryResultProxy(self.query).limit(2)
        assert_equals(['foo', 'bar'], self._names(self.proxy))
        
        self.proxy = QueryResultProxy(self.query).limit(20)
        assert_equals(['foo', 'bar', 'baz', 'quux', 'quuux'], self._names(self.proxy))
    
    def test_accepts_strings_for_limit(self):
        # that's what SQLAlchemy does (sic!)
        self.proxy = QueryResultProxy(self.query).limit('1')
        assert_equals(['foo'], self._names(self.proxy))
    
    # --- offset ---------------------------------------------------------------
    
    def test_can_offset_for_iteration(self):
        self.proxy = QueryResultProxy(self.query).offset(3)
        assert_equals(['quux', 'quuux'], self._names(self.proxy))
    
    def test_accepts_strings_for_offset(self):
        # that's what SQLAlchemy does (sic!)
        self.proxy = QueryResultProxy(self.query).offset('1')
        assert_equals(['bar', 'baz', 'quux', 'quuux'], self._names(self.proxy))
    
    # --- iteration ------------------------------------------------------------
    
    def test_can_iterate_over_results(self):
        filter_ = lambda item: item.activity >= 2
        self.proxy = QueryResultProxy(self.query, filter_=filter_)
        assert_true(hasattr(self.proxy, '__iter__'))
        
        results = list(self.proxy)
        assert_equals(['baz', 'quux', 'quuux'], self._names(results))
    
    # --- length ---------------------------------------------------------------
    
    def test_can_tell_length_if_no_more_items_available(self):
        filter_ = lambda item: item.activity >= 2
        self.proxy = QueryResultProxy(self.query, filter_=filter_)
        assert_true(hasattr(self.proxy, '__len__'))
        
        assert_length(3, self.proxy.fetch(10))
        assert_false(self.proxy.more_available())
        assert_length(3, self.proxy)
    
    def test_can_tell_length(self):
        filter_ = lambda item: item.activity >= 2
        self.proxy = QueryResultProxy(self.query, filter_=filter_)
        assert_length(3, self.proxy)
    
    def test_can_specify_how_many_items_should_be_fetched_by_default(self):
        self.proxy = QueryResultProxy(self.query, default_fetch=3)
        self.proxy.more_available()
        assert_equals(3, len(self.proxy._prefetched_items))
    
    # --- slicing --------------------------------------------------------------
    
    def test_supports_simple_slicing(self):
        assert_equals(['foo', 'bar'], self._names(self.proxy[0:2]))
        # slicing does not consume items
        assert_equals(['foo'], self._names([self.proxy.next()]))
        
        assert_equals(['baz', 'quux', 'quuux'], self._names(self.proxy[2:5]))
    
    # TODO: slice before start

import unittest
def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(QueryResultProxyTest))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='suite')
