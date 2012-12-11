# This file is a part of MediaCore CE, Copyright 2009-2012 MediaCore Inc.
# The source code contained in this file is licensed under the GPL.
# See LICENSE.txt in the main project directory, for more information.

from pylons import config, request

from mediacore.lib.auth.permission_system import MediaCorePermissionSystem


__all__ = ['viewable_media']

def viewable_media(query):
    permission_system = MediaCorePermissionSystem(config)
    return permission_system.filter_restricted_items(query, u'view', request.perm)

