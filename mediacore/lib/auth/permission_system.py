# This file is a part of MediaCore CE, Copyright 2009-2012 MediaCore Inc.
# The source code contained in this file is licensed under the GPL.
# See LICENSE.txt in the main project directory, for more information.

import re

from pylons.controllers.util import abort

from mediacore.lib.auth.api import PermissionSystem, UserPermissions
from mediacore.lib.auth.query_result_proxy import QueryResultProxy
from mediacore.model import DBSession, Group, User
from mediacore.plugin.abc import AbstractClass, abstractmethod


__all__ = ['MediaCorePermissionSystem', 'PermissionPolicies']

class PermissionPolicies(AbstractClass):
    @abstractmethod
    def permits(self, permission, perm, resource):
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


class MediaCorePermissionSystem(PermissionSystem):
    def __init__(self, config):
        policies = PermissionPolicies.configured_policies(config)
        super(MediaCorePermissionSystem, self).__init__(policies)
    
    @classmethod
    def permissions_for_request(cls, environ, config):
        identity = environ.get('repoze.who.identity', {})
        user_id = identity.get('repoze.who.userid')
        user = None
        if user_id is not None:
            user = DBSession.query(User).filter(User.user_id==user_id).first()
        return cls.permissions_for_user(user, config)
    
    @classmethod
    def permissions_for_user(cls, user, config):
        if user is None:
            user = User()
            user.display_name = u'Anonymous User'
            user.user_name = u'anonymous'
            user.email_address = 'invalid@mediacore.example'
            anonymous_group = Group.by_name(u'anonymous')
            groups = filter(None, [anonymous_group])
        else:
            authenticated_group = Group.by_name(u'authenticated')
            groups = list(user.groups) + filter(None, [authenticated_group])
        return UserPermissions(user, cls(config), groups=groups)
    
    def filter_restricted_items(self, query, permission_name, perm):
        can_access_item = \
            lambda item: perm.contains_permission(permission_name, item.resource)
        return QueryResultProxy(query, filter_=can_access_item)
    
    def raise_error(self, permission, resource):
        abort(404)

