# This file is a part of MediaCore CE, Copyright 2009-2012 MediaCore Inc.
# The source code contained in this file is licensed under the GPL.
# See LICENSE.txt in the main project directory, for more information.

from mediacore.lib.auth.api import IPermissionPolicy, UserPermissions
from mediacore.lib.auth.group_based_policy import GroupBasedPermissionsPolicy
from mediacore.lib.auth.permission_system import MediaCorePermissionSystem, PermissionPolicies
from mediacore.lib.test.db_testcase import DBTestCase
from mediacore.lib.test.pythonic_testcase import *
from mediacore.model import DBSession, Media, User


class FilteringRestrictedItemsTest(DBTestCase):
    def setUp(self):
        super(FilteringRestrictedItemsTest, self).setUp()
        
        # without explicit re-registration of the default policy unit tests 
        # failed when running 'python setup.py test'
        self._register_default_policy()
        # get rid of default media
        Media.query.delete()
        self.private_media = Media.example(slug=u'private')
        self.public_media = Media.example(slug=u'public')
        self.permission_system = MediaCorePermissionSystem(self.pylons_config)
        self.media_query = Media.query
        user = self._create_user_without_groups()
        self.perm = UserPermissions(user, self.permission_system)
    
    def _register_default_policy(self):
        PermissionPolicies.register(GroupBasedPermissionsPolicy)
    
    def _create_user_without_groups(self):
        user = User()
        user.user_name = u'joe'
        user.email_address = u'joe@mediacore.example'
        user.display_name = u'Joe'
        user.groups = []
        DBSession.add(user)
        DBSession.flush()
        return user
    
    # --- tests ---------------------------------------------------------------
    def test_can_use_policies_to_return_only_accessible_items(self):
        assert_equals(2, self.media_query.count())
        fake_policy = self._fake_view_policy(lambda media: (u'public' in media.slug))
        self.permission_system.policies = [fake_policy]
        
        results = self._media_query_results(u'view')
        assert_equals(1, results.count())
        assert_equals(self.public_media, list(results)[0])
    
    # --- helpers -------------------------------------------------------------
    
    def _media_query_results(self, permission):
        return self.permission_system.filter_restricted_items(self.media_query, permission, self.perm)
    
    def _fake_view_policy(self, condition):
        class FakeViewPolicy(IPermissionPolicy):
            permissions = (u'view', )
            
            def permits(self, permission, user_permissions, resource):
                media = resource.data['media']
                return condition(media)
        return FakeViewPolicy()


import unittest
def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(FilteringRestrictedItemsTest))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='suite')
