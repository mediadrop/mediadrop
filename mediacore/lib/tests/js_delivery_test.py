# -*- coding: utf-8 -*-
# This file is a part of MediaDrop (http://www.mediadrop.net),
# Copyright 2009-2013 MediaDrop contributors
# For the exact contribution history, see the git revision log.
# The source code in this file is is dual licensed under the MIT license or
# the GPLv3 or (at your option) any later version.
# See LICENSE.txt in the main project directory, for more information.

import re

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
        assert_equals(first, InlineJS('var a = %(a)s;', params=dict(a=42)))
    
    def test_can_tell_that_another_inlinescript_is_not_equal(self):
        first = InlineJS('var a = 42;')
        assert_not_equals(first, InlineJS('var a = null;'))
        assert_not_equals(first, InlineJS('var a  =  null;'))
        assert_not_equals(first, None)
    
    def test_can_render_as_html(self):
        assert_equals('<script type="text/javascript">var a = 42;</script>',
                      InlineJS('var a = 42;').render())
    
    def _js_code(self, script):
        match = re.search('^<script[^>]*?>(.*)</script>$', script.render())
        return match.group(1)
    
    def test_can_treat_js_as_template_and_inject_specified_parameters(self):
        script = InlineJS('var a = %(a)d;', params=dict(a=42))
        assert_equals('var a = 42;', self._js_code(script))
    
    def test_can_escape_string_parameters(self):
        script = InlineJS('var a = %(a)s;', params=dict(a='<script>'))
        assert_equals('var a = "\u003cscript\u003e";', self._js_code(script))
    
    def test_can_escape_list_parameter(self):
        script = InlineJS('var a = %(a)s;', params=dict(a=['<script>', 'b']))
        assert_equals('var a = ["\u003cscript\u003e", "b"];', self._js_code(script))
        
        script = InlineJS('var a = %(a)s;', params=dict(a=('<script>', 'b')))
        assert_equals('var a = ["\u003cscript\u003e", "b"];', self._js_code(script))
    
    def test_can_escape_dict_parameter(self):
        script = InlineJS('var a = %(a)s;', params=dict(a={'foo': '<script>'}))
        assert_equals('var a = {"foo": "\u003cscript\u003e"};', self._js_code(script))
    
    def test_does_not_escape_numbers(self):
        script = InlineJS('var a=%(a)d, b=%(b)s, c=%(c)0.2f;',
            params=dict(a=21, b=10l, c=1.5))
        assert_equals('var a=21, b=10, c=1.50;', self._js_code(script))
    
    def test_can_convert_simple_parameters(self):
        script = InlineJS('var a=%(a)s, b=%(b)s, c=%(c)s;',
          params=dict(a=True, b=False, c=None))
        assert_equals('var a=true, b=false, c=null;', self._js_code(script))
    
    def test_can_escape_nested_parameters_correctly(self):
        script = InlineJS('var a = %(a)s;', params=dict(a=[True, dict(b=12, c=["foo"])]))
        assert_equals('var a = [true, {"c": ["foo"], "b": 12}];', self._js_code(script))
     
    def test_raise_exception_for_unknown_parameters(self):
        script = InlineJS('var a = %(a)s;', params=dict(a=complex(2,3)))
        assert_raises(ValueError, script.render)


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
