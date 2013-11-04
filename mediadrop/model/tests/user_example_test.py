# This file is a part of MediaDrop (http://www.mediadrop.net),
# Copyright 2009-2013 MediaDrop contributors
# For the exact contribution history, see the git revision log.
# The source code contained in this file is licensed under the GPLv3 or
# (at your option) any later version.
# See LICENSE.txt in the main project directory, for more information.

from datetime import datetime, timedelta

from mediadrop.model import User
from mediadrop.lib.test.db_testcase import DBTestCase
from mediadrop.lib.test.pythonic_testcase import *


class UserExampleTest(DBTestCase):
    def test_can_create_example_user(self):
        user = User.example()
        
        assert_not_none(user.id)
        assert_equals(u'joe', user.user_name)
        assert_equals(u'Joe Smith', user.display_name)
        assert_equals(u'joe@site.example', user.email_address)
        assert_almost_equals(datetime.now(), user.created, 
                             max_delta=timedelta(seconds=1))
    
    def test_can_override_example_data(self):
        user = User.example(display_name=u'Bar Foo')
        
        assert_equals(u'Bar Foo', user.display_name)


import unittest
def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(UserExampleTest))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='suite')
