# -*- coding: utf-8 -*-
# This file is a part of MediaCore CE (http://www.mediacorecommunity.org),
# Copyright 2009-2013 MediaCore Inc., Felix Schwarz and other contributors.
# For the exact contribution history, see the git revision log.
# The source code contained in this file is licensed under the GPLv3 or
# (at your option) any later version.
# See LICENSE.txt in the main project directory, for more information.

from pylons import config

from mediacore.controllers.login import LoginController
from mediacore.lib.auth.permission_system import MediaCorePermissionSystem
from mediacore.lib.test import ControllerTestCase
from mediacore.lib.test.pythonic_testcase import *
from mediacore.model import DBSession, Group, User, Permission


class LoginControllerTest(ControllerTestCase):
    def test_non_editors_are_redirect_to_home_page_after_login(self):
        user = User.example()
        perm = MediaCorePermissionSystem.permissions_for_user(user, config)
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
    
    def test_uses_correct_redirect_url_if_mediacore_is_mounted_in_subdirectory(self):
        user = User.example()
        
        request = self.init_fake_request(server_name='server.example',
            request_uri='/login/post_login')
        request.environ['SCRIPT_NAME'] = 'my_media'
        
        response = self.call_post_login(user, request=request)
        assert_equals('http://server.example:80/my_media/', response.location)
    
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
