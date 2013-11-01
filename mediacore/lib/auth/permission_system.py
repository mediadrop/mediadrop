# This file is a part of MediaDrop (http://www.mediadrop.net),
# Copyright 2009-2013 MediaDrop contributors
# For the exact contribution history, see the git revision log.
# The source code contained in this file is licensed under the GPLv3 or
# (at your option) any later version.
# See LICENSE.txt in the main project directory, for more information.

import re

from pylons.controllers.util import abort
from sqlalchemy import or_

from mediacore.lib.auth.api import PermissionSystem, UserPermissions
from mediacore.lib.auth.query_result_proxy import QueryResultProxy, StaticQuery
from mediacore.model import DBSession, Group, User
from mediacore.plugin.abc import AbstractClass, abstractmethod


__all__ = ['MediaDropPermissionSystem', 'PermissionPolicies']

class PermissionPolicies(AbstractClass):
    @abstractmethod
    def permits(self, permission, perm, resource):
        pass
    
    @abstractmethod
    def can_apply_access_restrictions_to_query(self, query, permission):
        pass
    
    @abstractmethod
    def access_condition_for_query(self, query, permission, perm):
        pass
    
    @classmethod
    def configured_policies(cls, config):
        def policy_from_name(policy_name):
            for policy in cls:
                if policy.__name__ == policy_name:
                    return policy()
            raise AssertionError('No such policy: %s' % repr(policy_name))
        
        policy_names = re.split('\s*,\s*', config.get('permission_policies', ''))
        if policy_names == ['']:
            policy_names = ['GroupBasedPermissionsPolicy']
        return map(policy_from_name, policy_names)


class MediaDropPermissionSystem(PermissionSystem):
    def __init__(self, config):
        policies = PermissionPolicies.configured_policies(config)
        super(MediaDropPermissionSystem, self).__init__(policies)
    
    @classmethod
    def permissions_for_request(cls, environ, config):
        identity = environ.get('repoze.who.identity', {})
        user_id = identity.get('repoze.who.userid')
        user = None
        if user_id is not None:
            user = DBSession.query(User).filter(User.id==user_id).first()
        return cls.permissions_for_user(user, config)
    
    @classmethod
    def permissions_for_user(cls, user, config):
        if user is None:
            user = User()
            user.display_name = u'Anonymous User'
            user.user_name = u'anonymous'
            user.email_address = 'invalid@mediadrop.example'
            anonymous_group = Group.by_name(u'anonymous')
            groups = filter(None, [anonymous_group])
        else:
            meta_groups = Group.query.filter(Group.group_name.in_([u'anonymous', u'authenticated']))
            groups = list(user.groups) + list(meta_groups)
        return UserPermissions(user, cls(config), groups=groups)
    
    def filter_restricted_items(self, query, permission_name, perm):
        if self._can_apply_access_restrictions_to_query(query, permission_name):
            return self._apply_access_restrictions_to_query(query, permission_name, perm)
        
        can_access_item = \
            lambda item: perm.contains_permission(permission_name, item.resource)
        return QueryResultProxy(query, filter_=can_access_item)
    
    def raise_error(self, permission, resource):
        abort(404)
    # --- private API ---------------------------------------------------------
    
    def _can_apply_access_restrictions_to_query(self, query, permission_name):
        for policy in self.policies_for_permission(permission_name):
            if not policy.can_apply_access_restrictions_to_query(query, permission_name):
                return False
        return True
    
    def _apply_access_restrictions_to_query(self, query, permission_name, perm):
        conditions = []
        for policy in self.policies_for_permission(permission_name):
            result = policy.access_condition_for_query(query, permission_name, perm)
            if result == True:
                return QueryResultProxy(query)
            elif result == False:
                return StaticQuery([])
            elif result is None:
                continue
            
            condition = result
            if isinstance(result, tuple):
                condition, query = result
            conditions.append(condition)
        
        if len(conditions) == 0:
            # if there is no condition which can possibly allow the access, 
            # we should not return any items
            return StaticQuery([])
        restricted_query = query.distinct().filter(or_(*conditions))
        return QueryResultProxy(restricted_query)

