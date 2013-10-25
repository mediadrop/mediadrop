# -*- coding: utf-8 -*-
# This file is a part of MediaDrop (http://www.mediadrop.net),
# Copyright 2009-2013 MediaDrop contributors
# For the exact contribution history, see the git revision log.
# The source code contained in this file is licensed under the GPLv3 or
# (at your option) any later version.
# See LICENSE.txt in the main project directory, for more information.

from StringIO import StringIO

import simplejson

from mediacore.lib.attribute_dict import AttrDict
from mediacore.lib.players import AbstractFlashPlayer, FlowPlayer
from mediacore.lib.test import ControllerTestCase
from mediacore.lib.test.pythonic_testcase import *
from mediacore.model import fetch_row, Media


class UploadControllerTest(ControllerTestCase):
    def setUp(self):
        super(UploadControllerTest, self).setUp()
        AbstractFlashPlayer.register(FlowPlayer)
        FlowPlayer.inject_in_db(enable_player=True)
    
    def test_can_request_upload_form(self):
        request = self.init_fake_request(method='GET', request_uri='/upload')
        response = self._upload(request)
        assert_equals(200, response.status_int)
    
    def _upload(self, request):
        from mediacore.controllers.upload import UploadController
        response = self.call_controller(UploadController, request)
        return response
    
    def _upload_parameters(self):
        fake_file = StringIO('fake mp3 file content')
        parameters = dict(
            name = 'John Doe',
            email = 'john.doe@site.example',
            title = 'testing mp3 async upload',
            description = 'a great song',
            url = '',
            file = AttrDict(read=fake_file.read, filename='awesome-song.mp3'),
        )
        return parameters
    
    def _assert_succesful_media_upload(self):
        media = fetch_row(Media, slug=u'testing-mp3-async-upload')
        assert_equals('John Doe', media.author.name)
        assert_equals('john.doe@site.example', media.author.email)
        assert_equals('testing mp3 async upload', media.title)
        assert_equals('<p>a great song</p>', media.description)
        
        assert_length(1, media.files)
        media_file = media.files[0]
        assert_equals('mp3', media_file.container)
        assert_equals('awesome-song.mp3', media_file.display_name)
        return media
    
    def test_can_upload_file_with_js(self):
        request = self.init_fake_request(method='POST', request_uri='/upload/submit_async', 
            post_vars=self._upload_parameters())
        response = self._upload(request)
        
        assert_equals(200, response.status_int)
        assert_equals('application/json', response.headers['Content-Type'])
        assert_equals({'redirect': '/upload/success', 'success': True}, 
                      simplejson.loads(response.body))
        self._assert_succesful_media_upload()
    
    def test_can_submit_upload_with_plain_html_form(self):
        request = self.init_fake_request(method='POST', request_uri='/upload/submit', 
            post_vars=self._upload_parameters())
        response = self.assert_redirect(lambda: self._upload(request))
        assert_equals('http://mediadrop.example/upload/success', response.location)
        self._assert_succesful_media_upload()


import unittest

def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(UploadControllerTest))
    return suite
