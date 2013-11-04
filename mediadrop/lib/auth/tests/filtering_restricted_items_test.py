# This file is a part of MediaDrop (http://www.mediadrop.net),
# Copyright 2009-2013 MediaDrop contributors
# For the exact contribution history, see the git revision log.
# The source code contained in this file is licensed under the GPLv3 or
# (at your option) any later version.
# See LICENSE.txt in the main project directory, for more information.

from mediadrop.lib.auth.api import IPermissionPolicy, UserPermissions
from mediadrop.lib.auth.group_based_policy import GroupBasedPermissionsPolicy
from mediadrop.lib.auth.permission_system import MediaDropPermissionSystem, PermissionPolicies
from mediadrop.lib.test.db_testcase import DBTestCase
from mediadrop.lib.test.pythonic_testcase import *
from mediadrop.model import DBSession, Media, User


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
        self.permission_system = MediaDropPermissionSystem(self.pylons_config)
        self.media_query = Media.query
        user = self._create_user_without_groups()
        self.perm = UserPermissions(user, self.permission_system)
    
    def _register_default_policy(self):
        PermissionPolicies.register(GroupBasedPermissionsPolicy)
    
    def _create_user_without_groups(self):
        user = User()
        user.user_name = u'joe'
        user.email_address = u'joe@mediadrop.example'
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
    
    # --- tests with access filtering -----------------------------------------
    def test_can_add_filter_criteria_to_base_query(self):
        self.permission_system.policies = [
            self._fake_view_policy_with_query_conditions()
        ]
        results = self._media_query_results(u'view')
        assert_equals(1, results.count())
        assert_equals(self.private_media, list(results)[0])
        
        assert_equals(0, self._media_query_results(u'unknown').count())
    
    def test_only_adds_filter_criteria_to_query_if_all_policies_agree(self):
        self.permission_system.policies = [
            self._fake_view_policy_with_query_conditions(),
            self._fake_view_policy(lambda media: (u'public' in media.slug))
        ]
        results = self._media_query_results(u'view')
        assert_equals(1, results.count())
        assert_equals(self.public_media, list(results)[0])
    
    def test_policies_can_return_true_as_a_shortcut_to_prevent_further_result_filtering(self):
        class FakePolicy(IPermissionPolicy):
            permissions = (u'view', )
            
            def can_apply_access_restrictions_to_query(self, query, permission):
                return True
            
            def access_condition_for_query(self, query, permission, perm):
                return True
        self.permission_system.policies = [FakePolicy()]
        
        results = self._media_query_results(u'view')
        assert_equals(2, results.count())
    
    def test_policies_can_return_false_to_suppress_all_items(self):
        class FakePolicy(IPermissionPolicy):
            permissions = (u'view', )
            
            def can_apply_access_restrictions_to_query(self, query, permission):
                return True
            
            def access_condition_for_query(self, query, permission, perm):
                return False
        self.permission_system.policies = [FakePolicy()]
        
        results = self._media_query_results(u'view')
        assert_equals(0, results.count())
    
    def test_policies_can_return_none_as_access_condition(self):
        class FakePolicy(IPermissionPolicy):
            permissions = (u'view', )
            
            def can_apply_access_restrictions_to_query(self, query, permission):
                return True
            
            def access_condition_for_query(self, query, permission, perm):
                return None
        
        self.permission_system.policies = [FakePolicy()]
        results = self._media_query_results(u'view')
        assert_equals(0, results.count())
        
        self.permission_system.policies = [
            FakePolicy(), 
            self._fake_view_policy_with_query_conditions()
        ]
        results = self._media_query_results(u'view')
        assert_equals(1, results.count())
    
    def test_policies_can_return_query_and_condition(self):
        test_self = self
        class FakePolicy(IPermissionPolicy):
            permissions = (u'view', )
            
            def can_apply_access_restrictions_to_query(self, query, permission):
                return True
            
            def access_condition_for_query(self, query, permission, perm):
                query = query.filter(Media.id == test_self.private_media.id)
                return None, query
        self.permission_system.policies = [FakePolicy()]
        
        results = self._media_query_results(u'view')
        assert_equals(1, results.count())
        assert_equals(self.private_media, results.first())
    
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
    
    def _fake_view_policy_with_query_conditions(self):
        test_self = self
        class FakePolicy(IPermissionPolicy):
            permissions = (u'view', )
            
            def permits(self, permission, user_permissions, resource):
                return (resource.data['media'].id == test_self.public_media.id)
            
            def can_apply_access_restrictions_to_query(self, query, permission):
                return True
            
            def access_condition_for_query(self, query, permission, perm):
                return (Media.id == test_self.private_media.id)
        return FakePolicy()


import unittest
def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(FilteringRestrictedItemsTest))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='suite')
