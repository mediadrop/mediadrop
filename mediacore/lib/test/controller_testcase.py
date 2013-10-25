# -*- coding: utf-8 -*-
# This file is a part of MediaDrop (http://www.mediadrop.net),
# Copyright 2009-2013 MediaDrop contributors
# For the exact contribution history, see the git revision log.
# The source code contained in this file is licensed under the GPLv3 or
# (at your option) any later version.
# See LICENSE.txt in the main project directory, for more information.

from routes.util import URLGenerator
import pylons
from pylons.controllers.util import Response
from webob.exc import HTTPFound

from mediacore.lib.test.request_mixin import RequestMixin
from mediacore.lib.test.db_testcase import DBTestCase
from mediacore.lib.test.pythonic_testcase import *


__all__ = ['ControllerTestCase']

class ControllerTestCase(DBTestCase, RequestMixin):
    def call_controller(self, controller_class, request, user=None):
        controller = controller_class()
        controller._py_object = pylons
        if user or not hasattr(request, 'perm'):
            self.set_authenticated_user(user, request.environ)
        self._inject_url_generator_for_request(request)
        
        response_info = dict()
        def fake_start_response(status, headers, exc_info=None):
            response_info['status'] = status
            response_info['headerlist'] = headers
        response_body_lines = controller(request.environ, fake_start_response)
        
        template_vars = None
        if isinstance(response_body_lines, dict):
            template_vars = response_body_lines
            body = None
        else:
            body = '\n'.join(response_body_lines)
        response = Response(body=body, **response_info)
        response.template_vars = template_vars
        return response
    
    def assert_redirect(self, call_controller):
        try:
            response = call_controller()
        except Exception, e:
            if not isinstance(e, HTTPFound):
                raise
            response = e
        assert_equals(302, response.status_int)
        return response
    
    def _inject_url_generator_for_request(self, request):
        url_mapper = self.pylons_config['routes.map']
        url_generator = URLGenerator(url_mapper, request.environ)
        
        routes_dict = url_mapper.match(environ=request.environ)
        request.environ.update({
            'routes.url': url_generator,
            'wsgiorg.routing_args': (url_generator, routes_dict),
            'pylons.routes_dict': routes_dict,
        })
        return url_generator

