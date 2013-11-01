# This file is a part of MediaDrop (http://www.mediadrop.net),
# Copyright 2009-2013 MediaDrop contributors
# For the exact contribution history, see the git revision log.
# The source code contained in this file is licensed under the GPLv3 or
# (at your option) any later version.
# See LICENSE.txt in the main project directory, for more information.

from mediacore.lib.auth.api import UserPermissions
from mediacore.lib.auth.group_based_policy import GroupBasedPermissionsPolicy
from mediacore.lib.auth.permission_system import MediaDropPermissionSystem
from mediacore.lib.test.pythonic_testcase import *
from mediacore.lib.test.db_testcase import DBTestCase
from mediacore.model import DBSession, Media, Permission, User


class GroupBasedPermissionsPolicyTest(DBTestCase):
    def setUp(self):
        super(GroupBasedPermissionsPolicyTest, self).setUp()
        
        self.policy = GroupBasedPermissionsPolicy()
    
    def test_applies_to_all_permissions_in_db(self):
        Permission.example(name=u'custom')
        assert_contains(u'edit', self.policy.permissions)
        assert_contains(u'admin', self.policy.permissions)
        assert_contains(u'custom', self.policy.permissions)
    
    def perm(self):
        system = MediaDropPermissionSystem(self.pylons_config)
        system.policies = [self.policy]
        
        user = DBSession.query(User).filter(User.user_name == u'admin').one()
        return UserPermissions(user, system)
    
    def test_can_restrict_queries(self):
        query = Media.query
        permission = u'view'
        perm = self.perm()
        
        assert_true(self.policy.can_apply_access_restrictions_to_query(query, permission))
        assert_true(self.policy.access_condition_for_query(query, permission, perm))
    
    def test_can_restrict_query_if_user_does_not_have_the_required_permission(self):
        query = Media.query
        permission = u'view'
        perm = self.perm()
        view_permission = DBSession.query(Permission).filter(Permission.permission_name == permission).one()
        view_permission.groups = []
        DBSession.flush()
        
        assert_none(self.policy.access_condition_for_query(query, permission, perm))


import unittest
def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(GroupBasedPermissionsPolicyTest))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='suite')
