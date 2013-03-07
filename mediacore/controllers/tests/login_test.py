# -*- coding: utf-8 -*-
# This file is a part of MediaCore CE (http://www.mediacorecommunity.org),
# Copyright 2009-2013 MediaCore Inc., Felix Schwarz and other contributors.
# For the exact contribution history, see the git revision log.
# The source code contained in this file is licensed under the GPLv3 or
# (at your option) any later version.
# See LICENSE.txt in the main project directory, for more information.

import urlparse

from pylons import config
from webob.exc import HTTPFound

from mediacore.controllers.login import LoginController
from mediacore.lib.test.pythonic_testcase import *
from mediacore.model import DBSession, Group, User, Permission
from mediacore.lib.auth.permission_system import MediaCorePermissionSystem
from mediacore.lib.test.request_mixin import RequestMixin
from mediacore.lib.test.db_testcase import DBTestCase

import pylons
from pylons.controllers.util import Response
class ControllerTestCase(DBTestCase, RequestMixin):
    def call_controller(self, controller_class, request):
        controller = controller_class()
        controller._py_object = pylons
        
        response_info = dict()
        def fake_start_response(status, headers, exc_info=None):
            response_info['status'] = status
            response_info['headerlist'] = headers
        response_body_lines = controller(request.environ, fake_start_response)
        response = Response(body='\n'.join(response_body_lines), **response_info)
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

class LoginControllerTest(ControllerTestCase):
    def test_non_editors_are_redirect_to_home_page_after_login(self):
        user = User.example()
        perm = MediaCorePermissionSystem.permissions_for_user(user, config)
        assert_false(perm.contains_permission(u'edit'))
        assert_false(perm.contains_permission(u'admin'))
        
        response = self.call_post_login(user)
        redirect_path = urlparse.urlsplit(response.location)[2] # .path in 2.5+
        assert_equals('/', redirect_path)
    
    def test_admins_are_redirect_to_admin_area_after_login(self):
        admin = self._create_user_with_admin_permission_only()
        
        response = self.call_post_login(admin)
        redirect_path = urlparse.urlsplit(response.location)[2] # .path in 2.5+
        assert_equals('/admin', redirect_path)
    
    def test_editors_are_redirect_to_admin_area_after_login(self):
        editor = self._create_user_with_edit_permission_only()
        
        response = self.call_post_login(editor)
        redirect_path = urlparse.urlsplit(response.location)[2] # .path in 2.5+
        assert_equals('/admin', redirect_path)
    
    # - helpers ---------------------------------------------------------------
    
    def call_post_login(self, user):
        request = self.init_fake_request(method='GET')
        self.set_authenticated_user(user)
        
        request.environ['pylons.routes_dict'] = dict(
            action='post_login',
            controller=u'login',
        )
        response = self.assert_redirect(lambda: self.call_controller(LoginController, request))
        return response
    
    def editor_group(self):
        return DBSession.query(Group).filter(Group.group_name == u'editors').one()
    
    def _create_user_with_admin_permission_only(self):
        admin_perm = DBSession.query(Permission).filter(Permission.permission_name == u'admin').one()
        second_admin_group = Group.example(name=u'Second admin group')
        admin_perm.groups.append(second_admin_group)
        admin = User.example(groups=[second_admin_group])
        DBSession.commit()
        perm = MediaCorePermissionSystem.permissions_for_user(admin, config)
        assert_true(perm.contains_permission(u'admin'))
        assert_false(perm.contains_permission(u'edit'))
        return admin
    
    def _create_user_with_edit_permission_only(self):
        editor = User.example(groups=[self.editor_group()])
        perm = MediaCorePermissionSystem.permissions_for_user(editor, config)
        assert_true(perm.contains_permission(u'edit'))
        assert_false(perm.contains_permission(u'admin'))
        return editor


import unittest

def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(LoginControllerTest))
    return suite
