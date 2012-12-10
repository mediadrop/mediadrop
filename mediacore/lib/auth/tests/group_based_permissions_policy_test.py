# This file is a part of MediaCore CE, Copyright 2009-2012 MediaCore Inc.
# The source code contained in this file is licensed under the GPL.
# See LICENSE.txt in the main project directory, for more information.

from mediacore.lib.test.pythonic_testcase import *
from mediacore.lib.test.db_testcase import DBTestCase
from mediacore.lib.auth.group_based_policy import GroupBasedPermissionsPolicy
from mediacore.model.auth import Permission


class GroupBasedPermissionsPolicyTest(DBTestCase):
    def setUp(self):
        super(GroupBasedPermissionsPolicyTest, self).setUp()
        
        self.policy = GroupBasedPermissionsPolicy()
    
    def test_applies_to_all_permissions_in_db(self):
        Permission.example(name=u'custom')
        assert_contains(u'edit', self.policy.permissions)
        assert_contains(u'admin', self.policy.permissions)
        assert_contains(u'custom', self.policy.permissions)


import unittest
def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(GroupBasedPermissionsPolicyTest))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='suite')
