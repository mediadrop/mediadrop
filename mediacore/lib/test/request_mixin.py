# -*- coding: utf-8 -*-
# This file is a part of MediaCore CE, Copyright 2009-2012 MediaCore Inc.
# The source code in this file is dual licensed under the MIT license or the 
# GPL version 3 or (at your option) any later version.
# See LICENSE.txt in the main project directory, for more information.
#
# Copyright (c) 2012 Felix Schwarz <felix.schwarz@oss.schwarz.eu>

from cStringIO import StringIO
import urllib

from beaker.session import SessionObject
from paste.registry import Registry
import pylons
from pylons.controllers.util import Request, Response
from pylons.util import ContextObj
from routes.util import URLGenerator
import tw
from tw.mods.pylonshf import PylonsHostFramework
from webob.request import environ_from_url

from mediacore.config.middleware import create_tw_engine_manager
from mediacore.lib.auth.permission_system import MediaCorePermissionSystem
from mediacore.lib.paginate import Bunch


# -----------------------------------------------------------------------------
# unfortunately neither Python 2.4 nor any existing MediaCore dependencies come 
# with reusable methods to create a HTTP request body so I build a very basic 
# implementation myself. 
# The code is only used for unit tests so it doesn't have to be rock solid.
WWW_FORM_URLENCODED = 'application/x-www-form-urlencoded'

def encode_multipart_formdata(fields, files):
    lines = []
    BOUNDARY = '---some_random_boundary-string$'
    for key, value in fields:
        lines.extend([
            '--%s' % BOUNDARY,
            'Content-Disposition: form-data; name="%s"' % key,
            '',
            str(value)
        ])
    for key, file_ in files:
        if hasattr(file_, 'filename'):
            filename = file_.filename
        else:
            filename = file_.name
        lines.extend([
            '--%s' % BOUNDARY,
            'Content-Disposition: form-data; name="%s"; filename="%s"' % (key, filename),
            'Content-Type: application/octet-stream',
            '',
            file_.read()
        ])
    
    body = '\r\n'.join(lines)
    content_type = 'multipart/form-data; boundary=%s' % BOUNDARY
    return content_type, body


def build_http_body(data, force_multipart=False):
    if isinstance(data, basestring):
        return WWW_FORM_URLENCODED, data
    if hasattr(data, 'items'):
        data = data.items()
    
    fields = []
    files = []
    for key, value in data:
        if hasattr(value, 'read') and (hasattr(value, 'name') or hasattr(value, 'filename')):
            files.append((key, value))
        else:
            fields.append((key, value))
    if (not force_multipart) and len(files) == 0:
        return WWW_FORM_URLENCODED, urllib.urlencode(data)
    
    return encode_multipart_formdata(fields, files)
# -----------------------------------------------------------------------------

def create_wsgi_environ(url, request_method, request_body=None):
        wsgi_environ = environ_from_url(url)
        wsgi_environ.update({
            'REQUEST_METHOD': request_method,
        })
        if request_body:
            content_type, request_body = build_http_body(request_body)
            wsgi_environ.update({
                'wsgi.input': StringIO(request_body),
                'CONTENT_LENGTH': str(len(request_body)),
                'CONTENT_TYPE': content_type,
            })
        return wsgi_environ


class RequestMixin(object):
    def init_fake_request(self, server_name='mediacore.example', language='en', 
            method='GET', post_vars=None):
        app_globals = self.pylons_config['pylons.app_globals']
        pylons.app_globals._push_object(app_globals)
        
        if post_vars and method.upper() != 'POST':
            raise ValueError('You must not specify post_vars for request method %r' % method)
        wsgi_environ = create_wsgi_environ('http://%s' % server_name, 
            method.upper(), request_body=post_vars)
        request = Request(wsgi_environ, charset='utf-8')
        request.language = language
        request.settings = app_globals.settings
        pylons.request._push_object(request)
        response = Response(content_type='application/xml', charset='utf-8')
        pylons.response._push_object(response)
        
        session = SessionObject(wsgi_environ)
        pylons.session._push_object(session)

        routes_url = URLGenerator(self.pylons_config['routes.map'], wsgi_environ)
        pylons.url._push_object(routes_url)

        tmpl_context = ContextObj()
        tmpl_context.paginators = Bunch()
        pylons.tmpl_context._push_object(tmpl_context)
        # some parts of Pylons (e.g. Pylons.controllers.core.WSGIController)
        # use the '.c' alias instead.
        pylons.c = pylons.tmpl_context
        
        paste_registry = Registry()
        paste_registry.prepare()
        engines = create_tw_engine_manager(app_globals)
        host_framework = PylonsHostFramework(engines=engines)
        paste_registry.register(tw.framework, host_framework)
        
        wsgi_environ.update({
            'pylons.pylons': pylons,
            'paste.registry': paste_registry,
        })
        return request
    
    def set_authenticated_user(self, user, wsgi_environ=None):
        if wsgi_environ is None:
            wsgi_environ = pylons.request.environ
        
        identity = wsgi_environ.setdefault('repoze.who.identity', {})
        identity.update({
            'user': user,
            'repoze.who.userid': user.user_id,
        })
        perm = MediaCorePermissionSystem.permissions_for_request(wsgi_environ)
        wsgi_environ['mediacore.perm'] = perm
        pylons.request.perm = perm
    
    def remove_globals(self):
        for global_ in (pylons.request, pylons.response, pylons.session, 
                        pylons.tmpl_context, pylons.translator, pylons.url,):
            try:
                global_._pop_object()
            except AssertionError:
                # AssertionError: No object has been registered for this thread
                pass

