# -*- coding: utf-8 -*-
# This file is a part of MediaCore CE, Copyright 2009-2012 MediaCore Inc.
# The source code in this file is dual licensed under the MIT license or the 
# GPL version 3 or (at your option) any later version.
# See LICENSE.txt in the main project directory, for more information.
#
# Copyright (c) 2012 Felix Schwarz <felix.schwarz@oss.schwarz.eu>

from mediacore.lib.js_delivery import InlineJS, Script, Scripts
from mediacore.lib.test.pythonic_testcase import *


class ScriptTest(PythonicTestCase):
    def test_can_tell_if_another_script_is_equal(self):
        first = Script('/foo.js')
        second = Script('/foo.js')
        assert_equals(first, first)
        assert_equals(first, second)
        assert_equals(second, first)
    
    def test_can_tell_that_another_script_is_not_equal(self):
        first = Script('/foo.js')
        assert_not_equals(first, Script('/bar.js'))
        assert_not_equals(first, None)
    
    def test_can_render_as_html(self):
        assert_equals('<script src="/foo.js" type="text/javascript"></script>',
                      Script('/foo.js', async=False).render())
        assert_equals('<script src="/foo.js" async="async" type="text/javascript"></script>',
                      Script('/foo.js', async=True).render())


class InlineJSTest(PythonicTestCase):
    def test_can_tell_if_another_inlinescript_is_equal(self):
        first = InlineJS('var a = 42;')
        second = InlineJS('var a = 42;')
        assert_equals(first, first)
        assert_equals(first, second)
        assert_equals(second, first)
    
    def test_can_tell_that_another_inlinescript_is_not_equal(self):
        first = InlineJS('var a = 42;')
        assert_not_equals(first, InlineJS('var a = null;'))
        assert_not_equals(first, InlineJS('var a  =  null;'))
        assert_not_equals(first, None)
    
    def test_can_render_as_html(self):
        assert_equals('<script type="text/javascript">var a = 42;</script>',
                      InlineJS('var a = 42;').render())


class ScriptsTest(PythonicTestCase):
    # --- add scripts ----------------------------------------------------------
    def test_can_add_a_script(self):
        scripts = Scripts()
        scripts.add(Script('/foo.js'))
        assert_length(1, scripts)
    
    def test_can_multiple_scripts(self):
        scripts = Scripts()
        scripts.add_all(Script('/foo.js'), Script('/bar.js'))
        assert_length(2, scripts)
    
    def test_can_add_scripts_during_instantiation(self):
        scripts = Scripts(Script('/foo.js'), Script('/bar.js'))
        assert_length(2, scripts)

    # --- duplicate handling ---------------------------------------------------
    
    def test_does_not_add_duplicate_scripts(self):
        scripts = Scripts()
        scripts.add(Script('/foo.js'))
        scripts.add(Script('/foo.js'))
        assert_length(1, scripts)
        
    def test_uses_non_async_if_conflicting_variants_are_added(self):
        scripts = Scripts()
        scripts.add(Script('/foo.js', async=True))
        assert_length(1, scripts)
        assert_true(scripts.scripts[0].async)
        
        scripts.add(Script('/foo.js'))
        assert_length(1, scripts)
        assert_false(scripts.scripts[0].async)
    
    # --- replacing scripts ----------------------------------------------------

    def test_can_replace_script_with_key(self):
        foo_script = Script('/foo.js', key='foo')
        bar_script = Script('/bar.js', key='foo')
        
        scripts = Scripts()
        scripts.add(foo_script)
        scripts.replace_script_with_key(bar_script)
        assert_length(1, scripts)
        assert_contains(bar_script, scripts.scripts)
    
    # --- rendering ------------------------------------------------------------
    def test_can_render_markup_for_all_scripts(self):
        foo_script = Script('/foo.js')
        bar_script = Script('/bar.js')
        scripts = Scripts()
        scripts.add(foo_script)
        scripts.add(bar_script)
        assert_equals(foo_script.render()+bar_script.render(), scripts.render())



import unittest
def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ScriptTest))
    suite.addTest(unittest.makeSuite(InlineJSTest))
    suite.addTest(unittest.makeSuite(ScriptsTest))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='suite')
