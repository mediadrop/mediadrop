# -*- coding: utf-8 -*-
# This file is a part of MediaDrop (http://www.mediadrop.net),
# Copyright 2009-2013 MediaDrop contributors
# For the exact contribution history, see the git revision log.
# The source code in this file is is dual licensed under the MIT license or
# the GPLv3 or (at your option) any later version.
# See LICENSE.txt in the main project directory, for more information.

import cgi
from cStringIO import StringIO
import re

from mediadrop.lib.attribute_dict import AttrDict
from mediadrop.lib.helpers import has_permission
from mediadrop.lib.test.db_testcase import DBTestCase
from mediadrop.lib.test.pythonic_testcase import *
from mediadrop.lib.test import build_http_body, RequestMixin
from mediadrop.model import DBSession, User


class EncodeMultipartFormdataTest(PythonicTestCase):
    
    def encode_and_parse(self, values):
        content_type, body = build_http_body(values, force_multipart=True)
        boundary = re.search('multipart/form-data; boundary=(.+)$', content_type).group(1)
        parsed = cgi.parse_multipart(StringIO(body), {'boundary': boundary})
        
        results = dict()
        for key, values in parsed.items():
            assert_length(1, values)
            results[key] = values[0]
        return results
    
    def test_can_encode_simple_fields(self):
        results = self.encode_and_parse([('foo', 12), ('bar', 21)])
        assert_equals(dict(foo='12', bar='21'), results)
    
    def test_can_encode_simple_fields_from_dict(self):
        values = dict(foo='12', bar='21')
        
        results = self.encode_and_parse(values)
        assert_equals(values, results)
    
    def test_can_encode_file(self):
        fake_fp = AttrDict(name='foo.txt', read=lambda: 'foobar')
        results = self.encode_and_parse([('file', fake_fp)])
        assert_equals(dict(file='foobar'), results)


class FakeRequestWithAuthorizationTest(DBTestCase, RequestMixin):
    def test_can_fake_logged_in_user(self):
        admin = DBSession.query(User).filter(User.user_name==u'admin').one()
        assert_true(admin.has_permission(u'admin'))
        self.init_fake_request()
        self.set_authenticated_user(admin)
        
        assert_true(has_permission(u'admin'))


import unittest
def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(EncodeMultipartFormdataTest))
    suite.addTest(unittest.makeSuite(FakeRequestWithAuthorizationTest))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='suite')

