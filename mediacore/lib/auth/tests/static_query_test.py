# -*- coding: utf-8 -*-
# This file is a part of MediaDrop (http://www.mediadrop.net),
# Copyright 2009-2013 MediaDrop contributors
# For the exact contribution history, see the git revision log.
# The source code in this file is is dual licensed under the MIT license or
# the GPLv3 or (at your option) any later version.
# See LICENSE.txt in the main project directory, for more information.

from mediacore.lib.auth.query_result_proxy import StaticQuery
from mediacore.lib.test.pythonic_testcase import *


class StaticQueryTest(PythonicTestCase):
    def setUp(self):
        self.query = StaticQuery([1, 2, 3, 4, 5])
    
    def test_can_return_all_items(self):
        assert_equals([1, 2, 3, 4, 5], self.query.all())
    
    def test_can_return_all_items_with_iteration(self):
        assert_equals([1, 2, 3, 4, 5], list(self.query))
    
    def test_can_use_offset(self):
        assert_equals([3, 4, 5], self.query.offset(2).all())
    
    def test_can_build_static_query(self):
        assert_equals([1, 2], list(self.query.limit(2)))
    
    def test_knows_number_of_items(self):
        all_items = self.query.offset(1).all()
        assert_length(4, all_items)
        assert_equals(4, self.query.count())
        assert_equals(4, len(self.query))
    
    def test_supports_slicing(self):
        assert_equals([3, 4, 5], self.query[2:])
        assert_equals(3, self.query.offset(1)[2])
    
    def test_can_return_first_item(self):
        assert_equals(1, self.query.first())
        list(self.query) # consume all other items
        assert_none(self.query.first())


import unittest
def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(StaticQueryTest))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='suite')
