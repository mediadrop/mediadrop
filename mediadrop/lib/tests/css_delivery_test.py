# -*- coding: utf-8 -*-
# This file is a part of MediaDrop (http://www.mediadrop.net),
# Copyright 2009-2013 MediaDrop contributors
# For the exact contribution history, see the git revision log.
# The source code in this file is is dual licensed under the MIT license or
# the GPLv3 or (at your option) any later version.
# See LICENSE.txt in the main project directory, for more information.

from mediadrop.lib.css_delivery import StyleSheet, StyleSheets
from mediadrop.lib.test.pythonic_testcase import *


class StyleSheetTest(PythonicTestCase):
    def test_repr(self):
        assert_equals("StyleSheet('/foo.css', key=None)", repr(StyleSheet('/foo.css')))
        assert_equals("StyleSheet('/foo.css', key=None, media='screen')", 
                      repr(StyleSheet('/foo.css', media='screen')))
    
    def test_can_tell_if_another_script_is_equal(self):
        first = StyleSheet('/foo.css')
        second = StyleSheet('/foo.css')
        assert_equals(first, first)
        assert_equals(first, second)
        assert_equals(second, first)
        assert_equals(StyleSheet('/foo.css', media='screen'), 
                      StyleSheet('/foo.css', media='screen'))
    
    def test_can_tell_that_another_script_is_not_equal(self):
        first = StyleSheet('/foo.css')
        assert_not_equals(first, StyleSheet('/bar.css'))
        assert_not_equals(first, None)
        assert_not_equals(StyleSheet('/foo.css', media='screen'), 
                          StyleSheet('/foo.css', media='print'))
    
    def test_can_render_as_html(self):
        assert_equals('<link href="/foo.css" rel="stylesheet" type="text/css"></link>',
                      StyleSheet('/foo.css').render())
        assert_equals('<link href="/foo.css" rel="stylesheet" type="text/css" media="screen"></link>',
                      StyleSheet('/foo.css', media='screen').render())


class StyleSheetsTest(PythonicTestCase):
    # --- add stylesheets ----------------------------------------------------------
    def test_can_add_a_stylesheet(self):
        stylesheets = StyleSheets()
        stylesheets.add(StyleSheet('/foo.css'))
        assert_length(1, stylesheets)
    
    def test_can_multiple_stylesheets(self):
        scripts = StyleSheets()
        scripts.add_all(StyleSheet('/foo.css'), StyleSheet('/bar.css'))
        assert_length(2, scripts)

    def test_can_add_stylesheets_during_instantiation(self):
        stylesheets = StyleSheets(StyleSheet('/foo.css'), StyleSheet('/bar.css'))
        assert_length(2, stylesheets)

    # --- duplicate handling ---------------------------------------------------
    
    def test_does_not_add_duplicate_stylesheets(self):
        stylesheets = StyleSheets()
        stylesheets.add(StyleSheet('/foo.css'))
        stylesheets.add(StyleSheet('/foo.css'))
        assert_length(1, stylesheets)
    
    # --- replacing stylesheets ----------------------------------------------------

    def test_can_replace_stylesheet_with_key(self):
        foo_script = StyleSheet('/foo.css', key='foo')
        bar_script = StyleSheet('/bar.css', key='foo')
        
        stylesheets = StyleSheets()
        stylesheets.add(foo_script)
        stylesheets.replace_stylesheet_with_key(bar_script)
        assert_length(1, stylesheets)
        assert_contains(bar_script, stylesheets.stylesheets)
    
    # --- rendering ------------------------------------------------------------
    def test_can_render_markup_for_all_stylesheets(self):
        foo_script = StyleSheet('/foo.css')
        bar_script = StyleSheet('/bar.css')
        stylesheets = StyleSheets()
        stylesheets.add(foo_script)
        stylesheets.add(bar_script)
        assert_equals(unicode(foo_script)+unicode(bar_script), stylesheets.render())


import unittest
def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(StyleSheetTest))
    suite.addTest(unittest.makeSuite(StyleSheetsTest))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='suite')
