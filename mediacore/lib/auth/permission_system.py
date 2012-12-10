# This file is a part of MediaCore CE, Copyright 2009-2012 MediaCore Inc.
# The source code contained in this file is licensed under the GPL.
# See LICENSE.txt in the main project directory, for more information.

from pylons.controllers.util import abort

from mediacore.lib.auth.api import PermissionSystem, UserPermissions
from mediacore.lib.auth.group_based_policy import GroupBasedPermissionsPolicy
from mediacore.lib.auth.query_result_proxy import QueryResultProxy
from mediacore.model import DBSession, User


__all__ = ['MediaCorePermissionSystem']

class MediaCorePermissionSystem(PermissionSystem):
    def __init__(self):
        policies = (
            GroupBasedPermissionsPolicy(), 
        )
        super(MediaCorePermissionSystem, self).__init__(policies)
    
    @classmethod
    def permissions_for_request(cls, environ):
        identity = environ.get('repoze.who.identity', {})
        user_id = identity.get('repoze.who.userid')
        if user_id is not None:
            user = DBSession.query(User).filter(User.user_id==user_id).first()
        if user is None:
            user = User()
            user.display_name = u'Anonymous User'
            user.user_name = u'anonymous'
            user.email_address = 'invalid@mediacore.example'
            user.groups = []
        return cls.permissions_for_user(user)
    
    @classmethod
    def permissions_for_user(cls, user):
        return UserPermissions(user, MediaCorePermissionSystem())
    
    def filter_restricted_items(self, query, permission_name, perm):
        can_access_item = \
            lambda item: perm.contains_permission(permission_name, item.resource)
        return QueryResultProxy(query, filter_=can_access_item)
    
    def raise_error(self, permission, resource):
        abort(404)

