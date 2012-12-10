# This file is a part of MediaCore CE, Copyright 2009-2012 MediaCore Inc.
# The source code contained in this file is licensed under the GPL.
# See LICENSE.txt in the main project directory, for more information.

from mediacore.lib.auth.api import IPermissionPolicy
from mediacore.model import DBSession, Permission


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
