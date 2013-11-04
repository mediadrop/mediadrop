# -*- coding: utf-8 -*-
# This file is a part of MediaDrop (http://www.mediadrop.net),
# Copyright 2009-2013 MediaDrop contributors
# For the exact contribution history, see the git revision log.
# The source code contained in this file is licensed under the GPLv3 or
# (at your option) any later version.
# See LICENSE.txt in the main project directory, for more information.


from mediadrop.lib.test.db_testcase import DBTestCase
from mediadrop.lib.test.pythonic_testcase import *
from mediadrop.lib.test.request_mixin import RequestMixin


class DefaultPageTitleTest(DBTestCase, RequestMixin):
    def setUp(self):
        super(DefaultPageTitleTest, self).setUp()
        self.init_fake_request()
    
    def test_default_page_title_ignores_default_if_not_specified(self):
        # mediadrop.lib.helpers imports 'pylons.request' on class load time
        # so we import the symbol locally after we injected a fake request
        from mediadrop.lib.helpers import default_page_title
        assert_equals('MediaDrop', default_page_title())


import unittest
def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(DefaultPageTitleTest))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='suite')
