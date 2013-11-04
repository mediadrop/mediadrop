# This file is a part of MediaDrop (http://www.mediadrop.net),
# Copyright 2009-2013 MediaDrop contributors
# For the exact contribution history, see the git revision log.
# The source code contained in this file is licensed under the GPLv3 or
# (at your option) any later version.
# See LICENSE.txt in the main project directory, for more information.

from mediadrop.lib.attribute_dict import AttrDict
from mediadrop.lib.auth.api import IPermissionPolicy, PermissionSystem, Resource,\
    UserPermissions
from mediadrop.lib.test.pythonic_testcase import *


class PermissionSystemTest(PythonicTestCase):
    def setUp(self):
        self.system = PermissionSystem([])
        user = AttrDict(groups=[])
        self.perm = UserPermissions(user, self.system)
    
    def test_can_return_relevant_policies_for_permission(self):
        assert_length(0, self.system.policies_for_permission(u'foobar'))
        
        fake_policy = self._fake_policy(u'foobar', lambda r: True)
        self.system.policies = [fake_policy]
        
        assert_equals([fake_policy], 
                      self.system.policies_for_permission(u'foobar'))
        assert_length(0, self.system.policies_for_permission(u'unknown'))
    
    def test_can_tell_if_user_has_permission(self):
        self.system.policies = [self._fake_policy(u'view', lambda resource: resource.id == 1)]
        
        public_resource = Resource('foo', 1)
        private_resource = Resource(u'foo', 42)
        assert_true(self._has_permission(u'view', public_resource))
        assert_false(self._has_permission(u'view', private_resource))
    
    def test_restricts_access_if_no_policies_present(self):
        self.system.policies = []
        assert_false(self._has_permission(u'view', Resource('foo', 1)))
    
    def test_queries_next_policy_if_first_does_not_decides(self):
        def is_one_or_none(resource):
            if resource.id == 1:
                return True
            return None
        self.system.policies = [
            self._fake_policy(u'view', is_one_or_none),
            self._fake_policy(u'view', lambda r: r.id < 10),
        ]
        
        assert_true(self._has_permission(u'view', Resource('foo', 1)))
        assert_true(self._has_permission(u'view', Resource('foo', 5)))
        assert_false(self._has_permission(u'view', Resource('foo', 20)))
    
    def test_policy_can_block_access(self):
        self.system.policies = [
            self._fake_policy(u'view', lambda r: r.id == 1),
            self._fake_policy(u'view', lambda r: True),
        ]
        assert_true(self._has_permission(u'view', Resource('foo', 1)))
        assert_false(self._has_permission(u'view', Resource('foo', 2)))
    
    def test_asks_only_applicable_policies(self):
        self.system.policies = [self._fake_policy(u'view', lambda resource: resource.id == 1)]
        
        resource = Resource('foo', 1)
        assert_true(self._has_permission(u'view', resource))
        assert_false(self._has_permission(u'unknown', resource))
    
    # --- helpers -------------------------------------------------------------
    
    def _fake_policy(self, permission, condition):
        class FakePolicy(IPermissionPolicy):
            permissions = (permission, )
            
            def permits(self, permission, user_permissions, resource):
                return condition(resource)
        return FakePolicy()
    
    def _has_permission(self, permission, resource):
        return self.system.has_permission(permission, self.perm, resource)


import unittest
def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(PermissionSystemTest))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='suite')
