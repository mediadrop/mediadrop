# This file is a part of MediaDrop (http://www.mediadrop.net),
# Copyright 2009-2013 MediaDrop contributors
# For the exact contribution history, see the git revision log.
# The source code contained in this file is licensed under the GPLv3 or
# (at your option) any later version.
# See LICENSE.txt in the main project directory, for more information.

from pylons import config, request

from mediacore.lib.auth.permission_system import MediaDropPermissionSystem


__all__ = ['viewable_media']

def viewable_media(query):
    permission_system = MediaDropPermissionSystem(config)
    return permission_system.filter_restricted_items(query, u'view', request.perm)

