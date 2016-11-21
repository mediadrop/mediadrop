# -*- coding: utf-8 -*-
# This file is a part of MediaDrop (http://www.mediadrop.video),
# Copyright 2009-2014 MediaDrop contributors
# For the exact contribution history, see the git revision log.
# The source code contained in this file is licensed under the GPLv3 or
# (at your option) any later version.
# See LICENSE.txt in the main project directory, for more information.

from formencode.schema import Schema
from pylons import app_globals

from mediadrop.lib.test import *
from ..categories import CategoriesController


__all__ = ['APIAuthenticationTest']

class APIAuthenticationTest(ControllerTestCase, RequestMixin):
    def tearDown(self):
        self.remove_globals()
        super(APIAuthenticationTest, self).tearDown()
    
    def test_should_require_authentication(self):
        app_globals.settings['api_secret_key_required'] = 'true'
        
        request = self.init_fake_request(method='GET', request_uri='/api/categories')
        response = self.call_controller(CategoriesController, request)
        assert_equals(200, response.status_int)
        assert_contains('error', response.json)
        assert_equals('Authentication Error', response.json['error'])
    
    def test_should_list_results_when_authenticated(self):
        app_globals.settings['api_secret_key_required'] = 'true'
        app_globals.settings['api_secret_key'] = '12345'
        
        request = self.init_fake_request(method='GET', request_uri='/api/categories?api_key=12345')
        response = self.call_controller(CategoriesController, request)
        assert_equals(200, response.status_int)
        assert_not_contains('error', response.json)
        assert_contains('count', response.json)
        assert_equals(2, response.json['count'])
    
    def test_should_list_categories_when_no_authentication_is_required(self):
        app_globals.settings['api_secret_key_required'] = 'false'
        
        request = self.init_fake_request(method='GET', request_uri='/api/categories')
        response = self.call_controller(CategoriesController, request)
        assert_equals(200, response.status_int)
        assert_not_contains('error', response.json)
        assert_contains('count', response.json)
        assert_equals(2, response.json['count'])
    


def suite():
    import unittest
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(APIAuthenticationTest))
    return suite
