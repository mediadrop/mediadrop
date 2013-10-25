# -*- coding: utf-8 -*-
# This file is a part of MediaDrop (http://www.mediadrop.net),
# Copyright 2009-2013 MediaDrop contributors
# For the exact contribution history, see the git revision log.
# The source code contained in this file is licensed under the GPLv3 or
# (at your option) any later version.
# See LICENSE.txt in the main project directory, for more information.

from mediacore.lib.helpers import clean_xhtml, line_break_xhtml
from mediacore.lib.test.pythonic_testcase import *


class XHTMLNormalizationTest(PythonicTestCase):
    
    def test_can_replace_linebreaks_with_p_tags(self):
        htmlified_text = clean_xhtml('first\nline\n\nsecond line')
        assert_equals('<p>first line</p><p>second line</p>', htmlified_text)
        assert_equals(htmlified_text, clean_xhtml(htmlified_text))
    
    def test_trailing_newlines_are_removed_in_output(self):
        assert_equals(clean_xhtml('first\n'), clean_xhtml('first\n\n'))

    def test_text_do_not_change_after_a_clean_xhtml_and_line_break_xhtml_cycle(self):
        """Mimics the input -> clean -> display -> input... cycle of the 
        XHTMLTextArea widget.
        """
        expected_html = '<p>first line</p><p>second line</p>'
        htmlified_text = clean_xhtml('first\nline\n\nsecond line')
        assert_equals(expected_html, htmlified_text)
        
        # Ensure that re-cleaning the XHTML provides the same result.
        display_text = line_break_xhtml(htmlified_text)
        assert_equals('<p>first line</p>\n<p>second line</p>', display_text)
        assert_equals(expected_html, clean_xhtml(display_text))


import unittest
def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(XHTMLNormalizationTest))
    return suite

