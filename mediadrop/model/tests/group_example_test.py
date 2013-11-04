# This file is a part of MediaDrop (http://www.mediadrop.net),
# Copyright 2009-2013 MediaDrop contributors
# For the exact contribution history, see the git revision log.
# The source code contained in this file is licensed under the GPLv3 or
# (at your option) any later version.
# See LICENSE.txt in the main project directory, for more information.

from datetime import datetime, timedelta

from mediadrop.model import Group
from mediadrop.lib.test.db_testcase import DBTestCase
from mediadrop.lib.test.pythonic_testcase import *


class GroupExampleTest(DBTestCase):
    def test_can_create_example_group(self):
        group = Group.example()
        
        assert_not_none(group.group_id)
        assert_equals(u'baz_users', group.group_name)
        assert_equals(u'Baz Users', group.display_name)
        assert_almost_equals(datetime.now(), group.created, 
                             max_delta=timedelta(seconds=1))
    
    def test_can_override_example_data(self):
        group = Group.example(name=u'bar', display_name=u'Bar Foo')
        
        assert_equals(u'Bar Foo', group.display_name)
        assert_equals(u'bar', group.group_name)


import unittest
def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(GroupExampleTest))
    return suite
