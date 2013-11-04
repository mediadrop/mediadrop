# This file is a part of MediaDrop (http://www.mediadrop.net),
# Copyright 2009-2013 MediaDrop contributors
# For the exact contribution history, see the git revision log.
# The source code contained in this file is licensed under the GPLv3 or
# (at your option) any later version.
# See LICENSE.txt in the main project directory, for more information.

from mediadrop.lib.auth.api import IPermissionPolicy
from mediadrop.lib.auth.permission_system import PermissionPolicies
from mediadrop.model import DBSession, Permission


__all__ = ['GroupBasedPermissionsPolicy']

class GroupBasedPermissionsPolicy(IPermissionPolicy):
    @property
    def permissions(self):
        db_permissions = DBSession.query(Permission).all()
        return tuple([permission.permission_name for permission in db_permissions])
    
    def _permissions(self, perm):
        if 'permissions' not in perm.data:
            if perm.groups is None:
                return ()
            permissions = []
            for group in perm.groups:
                permissions.extend([p.permission_name for p in group.permissions])
            perm.data['permissions'] = permissions
        return perm.data['permissions']
    
    def permits(self, permission, perm, resource):
        if permission in self._permissions(perm):
            return True
        # there may be other policies still which can permit the access...
        return None
    
    def can_apply_access_restrictions_to_query(self, query, permission):
        return True
    
    def access_condition_for_query(self, query, permission, perm):
        if perm.contains_permission(permission):
            return True
        return None

PermissionPolicies.register(GroupBasedPermissionsPolicy)

