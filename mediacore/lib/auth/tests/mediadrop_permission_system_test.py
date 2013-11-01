# This file is a part of MediaDrop (http://www.mediadrop.net),
# Copyright 2009-2013 MediaDrop contributors
# For the exact contribution history, see the git revision log.
# The source code contained in this file is licensed under the GPLv3 or
# (at your option) any later version.
# See LICENSE.txt in the main project directory, for more information.

from mediacore.lib.auth.permission_system import MediaDropPermissionSystem
from mediacore.lib.test.db_testcase import DBTestCase
from mediacore.lib.test.pythonic_testcase import *
from mediacore.model.auth import Group, User
from mediacore.model.meta import DBSession


class MediaDropPermissionSystemTest(DBTestCase):
    def setUp(self):
        super(MediaDropPermissionSystemTest, self).setUp()
        
        self.anonymous = Group.by_name(u'anonymous')
        self.authenticated = Group.by_name(u'authenticated')
    
    def test_anonymous_users_belong_to_anonymous_group(self):
        self.assert_user_groups([self.anonymous], None)
    
    def test_authenticated_users_belong_to_anonymous_and_authenticated_groups(self):
        user = User.example()
        self.assert_user_groups([self.anonymous, self.authenticated], user)
    
    def test_metagroup_assignment_does_not_fail_if_groups_are_not_found_in_db(self):
        DBSession.delete(self.anonymous)
        DBSession.delete(self.authenticated)
        DBSession.flush()
        
        user = User.example()
        self.assert_user_groups([], user)
    
    # --- helpers -------------------------------------------------------------
    
    def assert_user_groups(self, groups, user):
        perm = MediaDropPermissionSystem.permissions_for_user(user, self.pylons_config)
        assert_equals(set(groups), set(perm.groups))


import unittest
def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(MediaDropPermissionSystemTest))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='suite')
