# This file is a part of MediaDrop (http://www.mediadrop.net),
# Copyright 2009-2013 MediaDrop contributors
# For the exact contribution history, see the git revision log.
# The source code contained in this file is licensed under the GPLv3 or
# (at your option) any later version.
# See LICENSE.txt in the main project directory, for more information.

import re

from pylons.controllers.util import Request
from routes.util import URLGenerator

from mediadrop.config.routing import add_routes, create_mapper
from mediadrop.lib.test.db_testcase import DBTestCase
from mediadrop.lib.test.pythonic_testcase import *
from mediadrop.lib.test.request_mixin import RequestMixin
from mediadrop.lib.test.support import create_wsgi_environ
from mediadrop.lib.util import current_url


class CurrentURLTest(DBTestCase, RequestMixin):
    def test_can_return_url(self):
        request = self.init_fake_request(server_name='server.example', request_uri='/media/view')
        self._inject_url_generator_for_request(request)
        assert_equals('/media/view', current_url(qualified=False))
        assert_equals('http://server.example:80/media/view', current_url(qualified=True))
    
    def _inject_url_generator_for_request(self, request):
        url_mapper = add_routes(create_mapper(self.pylons_config))
        url_generator = URLGenerator(url_mapper, request.environ)
        
        match = re.search('^.*?/([^/]+)(?:/([^/]+))?$', request.environ['PATH_INFO'])
        controller = match.group(1)
        action = match.group(2) or 'index'
        
        request.environ.update({
            'routes.url': url_generator,
            'wsgiorg.routing_args': (
                url_generator,
                dict(controller=controller, action=action),
            )
        })
        return url_generator
    
    def test_can_return_url_with_query_string(self):
        request = self.init_fake_request(server_name='server.example', 
            request_uri='/media/view?id=123')
        self._inject_url_generator_for_request(request)
        assert_equals('/media/view?id=123', current_url(qualified=False))
    
    def test_can_return_correct_url_even_for_whoopsidasy_page(self):
        user_url = 'http://server.example:8080/media/view?id=123'
        user_environ = create_wsgi_environ(user_url, 'GET')
        user_request = Request(user_environ, charset='utf-8')
        self._inject_url_generator_for_request(user_request)
        
        error_request = self.init_fake_request(request_uri='/error/document')
        self._inject_url_generator_for_request(error_request)
        error_request.environ['pylons.original_request'] = user_request
        
        assert_equals(user_url, current_url())
    
    def test_wsgi_deployment_in_a_subdirectory(self):
        request = self.init_fake_request(server_name='server.example', request_uri='/media/view')
        request.environ['SCRIPT_NAME'] = 'my_media'
        self._inject_url_generator_for_request(request)
        assert_equals('my_media/media/view', current_url(qualified=False))
    
    def test_proxy_deployment(self):
        self.pylons_config['proxy_prefix'] = '/proxy'
        request = self.init_fake_request(server_name='server.example', request_uri='/media/view')
        request.environ['SCRIPT_NAME'] = '/proxy'
        self._inject_url_generator_for_request(request)
        
        assert_equals('/proxy/media/view', current_url(qualified=False))


import unittest
def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(CurrentURLTest))
    return suite

