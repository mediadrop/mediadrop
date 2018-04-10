# -*- coding: utf-8 -*-
# This file is a part of MediaDrop (https://www.mediadrop.video),
# Copyright 2009-2018 MediaDrop contributors
# For the exact contribution history, see the git revision log.
# The source code in this file is dual licensed under the MIT license or
# the GPLv3 or (at your option) any later version.
# See LICENSE.txt in the main project directory, for more information.

from pythonic_testcase import *

from ..json_utilities import as_safe_json


class AsSafeJsonTest(PythonicTestCase):
    def test_returns_json_string_for_simple_python_types(self):
        assert_equals('1', as_safe_json(1))
        assert_equals('"foo"', as_safe_json(u'foo'))

    def test_can_escape_html_characters(self):
        assert_equals(
            '"\\u003cscript\\u003efoo\\u003c/script\\u003e"',
            as_safe_json(u'<script>foo</script>')
        )


import unittest
def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(AsSafeJsonTest))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='suite')
