# -*- coding: utf-8 -*-
# This file is a part of MediaDrop (http://www.mediadrop.net),
# Copyright 2009-2013 MediaDrop contributors
# For the exact contribution history, see the git revision log.
# The source code in this file is is dual licensed under the MIT license or
# the GPLv3 or (at your option) any later version.
# See LICENSE.txt in the main project directory, for more information.

from cStringIO import StringIO
import os
import urllib

from beaker.session import SessionObject
from paste.registry import Registry, StackedObjectProxy
import pylons
from pylons.controllers.util import Request, Response
from pylons.util import AttribSafeContextObj, ContextObj
from routes.util import URLGenerator
import tw
from tw.mods.pylonshf import PylonsHostFramework
from webob.request import environ_from_url

import mediadrop
from mediadrop.config.environment import load_environment
from mediadrop.config.middleware import create_tw_engine_manager
from mediadrop.lib.paginate import Bunch
from mediadrop.lib.i18n import Translator
from mediadrop.model.meta import DBSession, metadata


__all__ = [
    'build_http_body', 
    'create_wsgi_environ',
    'fake_request',
    'setup_environment_and_database',
]

def setup_environment_and_database(env_dir=None, enabled_plugins=''):
    global_config = {}
    env_dir = env_dir or '/invalid'
    app_config = {
        'plugins': enabled_plugins,
        'sqlalchemy.url': 'sqlite://',
        'layout_template': 'layout',
        'external_template': 'false',
        'image_dir': os.path.join(env_dir, 'images'),
        'media_dir': os.path.join(env_dir, 'media'),
    }
    pylons_config = load_environment(global_config, app_config)
    metadata.create_all(bind=DBSession.bind, checkfirst=True)
    return pylons_config

# -----------------------------------------------------------------------------
# unfortunately neither Python 2.4 nor any existing MediaDrop dependencies come
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


def setup_translator(language='en', registry=None, locale_dirs=None):
    if not locale_dirs:
        mediadrop_i18n_path = os.path.join(os.path.dirname(mediadrop.__file__), 'i18n')
        locale_dirs = {'mediadrop': mediadrop_i18n_path}
    translator = Translator(language, locale_dirs=locale_dirs)
    
    # not sure why but sometimes pylons.translator is not a StackedObjectProxy
    # but just a regular Translator.
    if not hasattr(pylons.translator, '_push_object'):
        pylons.translator = StackedObjectProxy()
    if registry is None:
        registry = pylons.request.environ['paste.registry']
    registry.replace(pylons.translator, translator)

def fake_request(pylons_config, server_name='mediadrop.example', language='en',
                 method='GET', request_uri='/', post_vars=None):
    app_globals = pylons_config['pylons.app_globals']
    pylons.app_globals._push_object(app_globals)
    
    if post_vars and method.upper() != 'POST':
        raise ValueError('You must not specify post_vars for request method %r' % method)
    wsgi_environ = create_wsgi_environ('http://%s%s' % (server_name, request_uri),
        method.upper(), request_body=post_vars)
    request = Request(wsgi_environ, charset='utf-8')
    request.language = language
    request.settings = app_globals.settings
    pylons.request._push_object(request)
    response = Response(content_type='application/xml', charset='utf-8')
    pylons.response._push_object(response)
    
    session = SessionObject(wsgi_environ)
    pylons.session._push_object(session)

    routes_url = URLGenerator(pylons_config['routes.map'], wsgi_environ)
    pylons.url._push_object(routes_url)

    # Use ContextObj() when we get rid of 'pylons.strict_tmpl_context=False' in
    # mediadrop.lib.environment
    tmpl_context = AttribSafeContextObj()
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
    setup_translator(language=language, registry=paste_registry,
        locale_dirs=pylons_config.get('locale_dirs'))
    
    wsgi_environ.update({
        'pylons.pylons': pylons,
        'paste.registry': paste_registry,
    })
    return request
