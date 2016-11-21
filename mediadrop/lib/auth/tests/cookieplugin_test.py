# -*- coding: utf-8 -*-
# This file is a part of MediaDrop (http://www.mediadrop.video),
# Copyright 2009-2015 MediaDrop contributors
# For the exact contribution history, see the git revision log.
# The source code in this file is dual licensed under the MIT license or
# the GPLv3 or (at your option) any later version.
# See LICENSE.txt in the main project directory, for more information.

from mediadrop.lib.auth.middleware import MediaDropCookiePlugin
from mediadrop.lib.test import create_wsgi_environ
from mediadrop.lib.test.pythonic_testcase import *


class MediaDropCookiePluginTest(PythonicTestCase):
    def test_sets_cookie_expiry_based_on_session_timeout(self):
        cookie_plugin = self._cookie_plugin()
        environ = self._wsgi_env(cookie_plugin=None)
        assert_none(cookie_plugin.identify(environ))

        environ = self._wsgi_env(cookie_plugin=cookie_plugin)
        identity = cookie_plugin.identify(environ)
        assert_not_none(identity)
        assert_contains('max_age', identity,
            message='The max_age parameter will cause repoze.who/AuthTkt to set an expiration date for the cookie')

    def _cookie_plugin(self):
        return MediaDropCookiePlugin('secret',
            cookie_name='foo',
            timeout=100,
            reissue_time=100/2,
        )

    def _wsgi_env(self, cookie_plugin=None):
        with_cookie = (cookie_plugin is not None)
        env = create_wsgi_environ('http://server.example', 'GET')
        if with_cookie:
            cookie_plugin = self._cookie_plugin()
            identity = {'repoze.who.userid': 20}
            headers = cookie_plugin.remember(env.copy(), identity)
            assert_length(3, headers) # multiple headers for different paths
            cookie_value = headers[0][1]
            env['HTTP_COOKIE'] = cookie_value
            return env
        return env

import unittest
def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(MediaDropCookiePluginTest))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='suite')
