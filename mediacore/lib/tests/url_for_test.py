# This file is a part of MediaDrop (http://www.mediadrop.net),
# Copyright 2009-2013 MediaDrop contributors
# For the exact contribution history, see the git revision log.
# The source code contained in this file is licensed under the GPLv3 or
# (at your option) any later version.
# See LICENSE.txt in the main project directory, for more information.

from mediacore.lib.test.db_testcase import DBTestCase
from mediacore.lib.test.pythonic_testcase import *
from mediacore.lib.test.request_mixin import RequestMixin
from mediacore.lib.util import url_for


class URLForTest(DBTestCase, RequestMixin):
    def test_can_generate_static_url_with_proxy_prefix(self):
        self.pylons_config['proxy_prefix'] = '/proxy'
        request = self.init_fake_request(server_name='server.example')
        request.environ['SCRIPT_NAME'] = '/proxy'
        
        assert_equals('/proxy/media', url_for('/media'))
        qualified_media_url = url_for('/media', qualified=True)
        assert_equals('http://server.example:80/proxy/media', qualified_media_url)


import unittest
def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(URLForTest))
    return suite

