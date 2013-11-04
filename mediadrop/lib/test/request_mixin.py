# -*- coding: utf-8 -*-
# This file is a part of MediaDrop (http://www.mediadrop.net),
# Copyright 2009-2013 MediaDrop contributors
# For the exact contribution history, see the git revision log.
# The source code in this file is is dual licensed under the MIT license or
# the GPLv3 or (at your option) any later version.
# See LICENSE.txt in the main project directory, for more information.

import pylons

from mediadrop.lib.auth.permission_system import MediaDropPermissionSystem
from mediadrop.lib.test.support import fake_request


__all__ = ['RequestMixin']

class RequestMixin(object):
    def init_fake_request(self, **kwargs):
        return fake_request(self.pylons_config, **kwargs)
    
    def set_authenticated_user(self, user, wsgi_environ=None):
        if wsgi_environ is None:
            wsgi_environ = pylons.request.environ
        
        if (user is None) and ('repoze.who.identity' in wsgi_environ):
            del wsgi_environ['repoze.who.identity']
        elif user is not None:
            identity = wsgi_environ.setdefault('repoze.who.identity', {})
            identity.update({
                'user': user,
                'repoze.who.userid': user.id,
            })
        perm = MediaDropPermissionSystem.permissions_for_request(wsgi_environ, self.pylons_config)
        wsgi_environ['mediadrop.perm'] = perm
        pylons.request.perm = perm
    
    def remove_globals(self):
        for global_ in (pylons.request, pylons.response, pylons.session, 
                        pylons.tmpl_context, pylons.translator, pylons.url,):
            try:
                if hasattr(global_, '_pop_object'):
                    global_._pop_object()
            except AssertionError:
                # AssertionError: No object has been registered for this thread
                pass

