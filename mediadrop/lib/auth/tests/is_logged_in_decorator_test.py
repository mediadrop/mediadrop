# This file is a part of MediaDrop (http://www.mediadrop.video),
# Copyright 2009-2015 MediaDrop contributors
# For the exact contribution history, see the git revision log.
# The source code contained in this file is licensed under the GPLv3 or
# (at your option) any later version.
# See LICENSE.txt in the main project directory, for more information.

from mediadrop.lib.auth.pylons_glue import is_logged_in
from mediadrop.lib.test import DBTestCase, RequestMixin
from mediadrop.lib.test.pythonic_testcase import *
from mediadrop.model import User

class IsLoggedInDecoratorTest(DBTestCase, RequestMixin):
    def test_permits_access_if_user_is_logged_in(self):
        request = self.init_fake_request()
        self.set_authenticated_user(User.example())
        assert_true(is_logged_in().has_required_permission(request))
    
    def test_denies_access_to_anonymous_users(self):
        request = self.init_fake_request()
        assert_false(is_logged_in().has_required_permission(request))


import unittest
def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(IsLoggedInDecoratorTest))
    return suite
