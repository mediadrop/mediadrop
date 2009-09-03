# -*- coding: utf-8 -*-

from simpleplex.tests import TestController
from nose.tools import assert_true

# This is an example of how you can write functional tests for your controller.
# As opposed to a pure unit-test which test a small unit of functionallity,
# these functional tests exercise the whole app and it's WSGI stack.
# Please read http://pythonpaste.org/webtest/ for more information

class TestRootController(TestController):
    def test_index(self):
        response = self.app.get('/')
        msg = 'TurboGears 2 is rapid web application development toolkit '\
              'designed to make your life easier.'
        # You can look for specific strings:
        assert_true(msg in response)
        # You can also access a BeautifulSoup'ed version
        # first run $ easy_install BeautifulSoup and then run this test 
        links = response.html.findAll('a')
        assert_true(links, "Mummy, there are no links here!")
