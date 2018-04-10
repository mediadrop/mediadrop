# -*- coding: utf-8 -*-
# This file is a part of MediaDrop (https://www.mediadrop.video),
# Copyright 2009-2018 MediaDrop contributors
# For the exact contribution history, see the git revision log.
# The source code in this file is dual licensed under the MIT license or
# the GPLv3 or (at your option) any later version.
# See LICENSE.txt in the main project directory, for more information.

from pythonic_testcase import *

from ..css_delivery import Stylesheet, Stylesheets


class StylesheetTest(PythonicTestCase):
    def test_repr(self):
        assert_equals("Stylesheet('/foo.css', key=None)", repr(Stylesheet('/foo.css')))
        assert_equals("Stylesheet('/foo.css', key=None, media='screen')",
                      repr(Stylesheet('/foo.css', media='screen')))

    def test_can_tell_if_another_script_is_equal(self):
        first = Stylesheet('/foo.css')
        second = Stylesheet('/foo.css')
        assert_equals(first, first)
        assert_equals(first, second)
        assert_equals(second, first)
        assert_equals(Stylesheet('/foo.css', media='screen'),
                      Stylesheet('/foo.css', media='screen'))

    def test_can_tell_that_another_script_is_not_equal(self):
        first = Stylesheet('/foo.css')
        assert_not_equals(first, Stylesheet('/bar.css'))
        assert_not_equals(first, None)
        assert_not_equals(Stylesheet('/foo.css', media='screen'),
                          Stylesheet('/foo.css', media='print'))

    def test_stylesheets_with_the_same_key_are_considered_equal(self):
        first = Stylesheet('/foo/library.css', key='library')
        second = Stylesheet('/bar/library.css', key='library')
        assert_equals(first, second)

        second.key = 'lib2'
        assert_not_equals(first, second)

    def test_can_render_as_html(self):
        assert_equals('<link href="/foo.css" rel="stylesheet" type="text/css"></link>',
                      Stylesheet('/foo.css').render())
        assert_equals('<link href="/foo.css" rel="stylesheet" type="text/css" media="screen"></link>',
                      Stylesheet('/foo.css', media='screen').render())


class StylesheetsTest(PythonicTestCase):
    # --- add stylesheets ----------------------------------------------------------
    def test_can_add_a_stylesheet(self):
        stylesheets = Stylesheets()
        stylesheets.add(Stylesheet('/foo.css'))
        assert_length(1, stylesheets)

    def test_can_multiple_stylesheets(self):
        scripts = Stylesheets()
        scripts.add_all(Stylesheet('/foo.css'), Stylesheet('/bar.css'))
        assert_length(2, scripts)

    def test_can_add_stylesheets_during_instantiation(self):
        stylesheets = Stylesheets(Stylesheet('/foo.css'), Stylesheet('/bar.css'))
        assert_length(2, stylesheets)

    # --- duplicate handling ---------------------------------------------------

    def test_does_not_add_duplicate_stylesheets(self):
        stylesheets = Stylesheets()
        stylesheets.add(Stylesheet('/foo.css'))
        stylesheets.add(Stylesheet('/foo.css'))
        assert_length(1, stylesheets)

    # --- replacing stylesheets ----------------------------------------------------

    def test_can_replace_stylesheet_with_key(self):
        foo_script = Stylesheet('/foo.css', key='foo')
        bar_script = Stylesheet('/bar.css', key='foo')

        stylesheets = Stylesheets()
        stylesheets.add(foo_script)
        stylesheets.replace_stylesheet_with_key(bar_script)
        assert_length(1, stylesheets)
        assert_contains(bar_script, stylesheets.stylesheets)

    # --- rendering ------------------------------------------------------------
    def test_can_render_markup_for_all_stylesheets(self):
        foo_script = Stylesheet('/foo.css')
        bar_script = Stylesheet('/bar.css')
        stylesheets = Stylesheets()
        stylesheets.add(foo_script)
        stylesheets.add(bar_script)
        assert_equals(unicode(foo_script)+unicode(bar_script), stylesheets.render())


import unittest
def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(StylesheetTest))
    suite.addTest(unittest.makeSuite(StylesheetsTest))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='suite')
