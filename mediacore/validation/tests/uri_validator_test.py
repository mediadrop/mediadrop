# -*- coding: utf-8 -*-
# This file is a part of MediaDrop (http://www.mediadrop.net),
# Copyright 2009-2013 MediaDrop contributors
# For the exact contribution history, see the git revision log.
# The source code contained in this file is licensed under the GPLv3 or
# (at your option) any later version.
# See LICENSE.txt in the main project directory, for more information.

from formencode.api import Invalid

from mediacore.lib.test import *
from mediacore.validation import URIValidator


__all__ = ['URIValidatorTest']

class URIValidatorTest(DBTestCase, RequestMixin):
    def setUp(self):
        super(URIValidatorTest, self).setUp()
        # set's up pylons.translator
        self.init_fake_request()
        self.validator = URIValidator()
    
    def tearDown(self):
        self.remove_globals()
        super(URIValidatorTest, self).tearDown()
    
    def to_python(self, value):
        return self.validator.to_python(value)
    
    def test_accepts_http_url(self):
        url = u'http://site.example/foo/video.ogv'
        assert_equals(url, self.to_python(url))
    
    def test_accepts_rtmp_url(self):
        url = u'rtmp://site.example/foo/video.ogv'
        assert_equals(url, self.to_python(url))
    
    def assert_invalid(self, value):
        return assert_raises(Invalid, lambda: self.to_python(value))
    
    def test_rejects_invalid_url(self):
        self.assert_invalid(u'invalid')
        self.assert_invalid(u'http://?foo=bar')
        # important to check details of the Python 2.4 urlsplit workaround
        self.assert_invalid(u'rtmp://')
        self.assert_invalid(u'rtmp:')


def suite():
    import unittest
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(URIValidatorTest))
    return suite

