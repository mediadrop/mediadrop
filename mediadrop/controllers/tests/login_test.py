# -*- coding: utf-8 -*-
# This file is a part of MediaDrop (http://www.mediadrop.video),
# Copyright 2009-2015 MediaDrop contributors
# For the exact contribution history, see the git revision log.
# The source code contained in this file is licensed under the GPLv3 or
# (at your option) any later version.
# See LICENSE.txt in the main project directory, for more information.

import urllib

from ddt import ddt as DataDrivenTestCase, data
from pylons import config

from mediadrop.controllers.login import LoginController
from mediadrop.lib.auth.permission_system import MediaDropPermissionSystem
from mediadrop.lib.test import ControllerTestCase
from mediadrop.lib.test.pythonic_testcase import *
from mediadrop.model import DBSession, Group, User, Permission


@DataDrivenTestCase
class LoginControllerTest(ControllerTestCase):
    def test_non_editors_are_redirect_to_home_page_after_login(self):
        user = User.example()
        perm = MediaDropPermissionSystem.permissions_for_user(user, config)
        assert_false(perm.contains_permission(u'edit'))
        assert_false(perm.contains_permission(u'admin'))
        
        response = self.call_post_login(user)
        assert_equals('http://server.example:80/', response.location)
    
    def test_admins_are_redirect_to_admin_area_after_login(self):
        admin = self._create_user_with_admin_permission_only()
        
        response = self.call_post_login(admin)
        assert_equals('http://server.example:80/admin', response.location)
    
    def test_editors_are_redirect_to_admin_area_after_login(self):
        editor = self._create_user_with_edit_permission_only()
        
        response = self.call_post_login(editor)
        assert_equals('http://server.example:80/admin', response.location)
    
    def test_uses_correct_redirect_url_if_mediadrop_is_mounted_in_subdirectory(self):
        user = User.example()
        
        request = self.init_fake_request(server_name='server.example',
            request_uri='/login/post_login')
        request.environ['SCRIPT_NAME'] = 'my_media'
        
        response = self.call_post_login(user, request=request)
        assert_equals('http://server.example:80/my_media/', response.location)
    
    def test_ignores_redirect_url_if_target_action_does_not_allow_get_requests(self):
        admin = self._create_user_with_admin_permission_only()
        user_save_url = 'http://server.example:80/admin/users/%d/save' % admin.id
        came_from = urllib.quote_plus(user_save_url)
        request = self.init_fake_request(server_name='server.example',
            request_uri='/login/post_login?came_from='+came_from)
        response = self.call_post_login(admin, request=request)
        assert_equals('http://server.example:80/admin', response.location,
            message='should just ignore came_from for post-only targets.')
    
    def test_prevent_parameter_base_redirection(self):
        user = User.example()

        came_from = urllib.quote_plus('http://evil.site/malware/')
        request = self.init_fake_request(server_name='server.example',
            request_uri='/login/post_login?came_from='+came_from)
        response = self.call_post_login(user, request=request)
        assert_equals('http://server.example:80/', response.location,
            message='should only redirect to urls on the same domain')
    
    @data('http://server.example', 'http://server.example:80',
          'http://server.example/media' 'http://server.example:80/media',
          'http://server.example/cms/', 'http://server.example:80/cms',
          'https://server.example/', 'https://server.example:443/',
          'https://server.example/external/', 'https://server.example:443/external/',
          'http://server.example:8080',
          )
    def test_can_redirect_to_domains_on_same_domain_after_login(self, came_from):
        user = User.example()
        quoted_came_from = urllib.quote_plus(came_from)
        request = self.init_fake_request(server_name='server.example',
            request_uri='/login/post_login?came_from='+quoted_came_from)
        response = self.call_post_login(user, request=request)
        assert_equals(came_from, response.location)
    
    def test_handles_bad_came_from_parameter_gracefully(self):
        user = User.example()
        quoted_came_from = urllib.quote_plus('invalid junk')
        request = self.init_fake_request(server_name='server.example',
            request_uri='/login/post_login?came_from='+quoted_came_from)
        response = self.call_post_login(user, request=request)
        assert_equals('http://server.example:80/', response.location)

    # - helpers ---------------------------------------------------------------
    
    def call_post_login(self, user, request=None):
        if request is None:
            request = self.init_fake_request(method='GET', 
                server_name='server.example', request_uri='/login/post_login')
        self.set_authenticated_user(user)
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
        perm = MediaDropPermissionSystem.permissions_for_user(admin, config)
        assert_true(perm.contains_permission(u'admin'))
        assert_false(perm.contains_permission(u'edit'))
        return admin
    
    def _create_user_with_edit_permission_only(self):
        editor = User.example(groups=[self.editor_group()])
        perm = MediaDropPermissionSystem.permissions_for_user(editor, config)
        assert_true(perm.contains_permission(u'edit'))
        assert_false(perm.contains_permission(u'admin'))
        return editor


import unittest

def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(LoginControllerTest))
    return suite
