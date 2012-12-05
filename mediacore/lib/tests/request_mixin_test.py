# -*- coding: utf-8 -*-
# This file is a part of MediaCore CE, Copyright 2009-2012 MediaCore Inc.
# The source code in this file is dual licensed under the MIT license or the 
# GPL version 3 or (at your option) any later version.
# See LICENSE.txt in the main project directory, for more information.
#
# Copyright (c) 2012 Felix Schwarz <felix.schwarz@oss.schwarz.eu>

import cgi
from cStringIO import StringIO
import re

from mediacore.lib.attribute_dict import AttrDict
from mediacore.lib.test.pythonic_testcase import *
from mediacore.lib.test.request_mixin import build_http_body


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

import unittest
def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(EncodeMultipartFormdataTest))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='suite')

