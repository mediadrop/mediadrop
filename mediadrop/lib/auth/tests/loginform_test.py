# -*- coding: utf-8 -*-
# This file is a part of MediaDrop (http://www.mediadrop.video),
# Copyright 2009-2015 MediaDrop contributors
# For the exact contribution history, see the git revision log.
# The source code in this file is dual licensed under the MIT license or
# the GPLv3 or (at your option) any later version.
# See LICENSE.txt in the main project directory, for more information.

from mediadrop.config.routing import login_form_url, login_handler_url, \
    logout_handler_url, post_login_url, post_logout_url
from mediadrop.lib.auth.middleware import MediaDropLoginForm
from mediadrop.lib.test import create_wsgi_environ
from mediadrop.lib.test.pythonic_testcase import *


class MediaDropLoginFormTest(PythonicTestCase):
    def test_sets_max_age_for_successful_logins(self):
        form = self._form()
        environ = self._wsgi_env(with_credentials=False)
        assert_none(form.identify(environ))

        environ = self._wsgi_env(with_credentials=True)
        identity = form.identify(environ)
        assert_not_none(identity)
        assert_contains('max_age', identity,
            message='should remember login session for some time')

    def _form(self):
        return MediaDropLoginForm(
            login_form_url,
            login_handler_url,
            post_login_url,
            logout_handler_url,
            post_logout_url,
            rememberer_name='cookie',
            charset='utf-8',
        )

    def _wsgi_env(self, with_credentials=True):
        url = 'http://server.example'
        if not with_credentials:
            return create_wsgi_environ(url, 'POST')
        return create_wsgi_environ(url + login_handler_url, 'POST',
            request_body={'login': 'foo', 'password': 'bar'})

import unittest
def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(MediaDropLoginFormTest))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='suite')
