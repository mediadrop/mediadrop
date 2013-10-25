# -*- coding: utf-8 -*-
# This file is a part of MediaDrop (http://www.mediadrop.net),
# Copyright 2009-2013 MediaDrop contributors
# For the exact contribution history, see the git revision log.
# The source code contained in this file is licensed under the GPLv3 or
# (at your option) any later version.
# See LICENSE.txt in the main project directory, for more information.

from formencode.schema import Schema
from pylons import app_globals

from mediacore.lib.test import *
from mediacore.validation import LimitFeedItemsValidator


__all__ = ['LimitFeedItemsValidator']

class LimitFeedItemsValidatorTest(DBTestCase, RequestMixin):
    def setUp(self):
        super(LimitFeedItemsValidatorTest, self).setUp()
        self.init_fake_request()
        # just to be sure all settings have been cleared.
        assert_none(app_globals.settings.get('default_feed_results'))
        app_globals.settings['default_feed_results'] = 42
        self.validator = LimitFeedItemsValidator()
    
    def tearDown(self):
        self.remove_globals()
        super(LimitFeedItemsValidatorTest, self).tearDown()
    
    def to_python(self, value):
        return self.validator.to_python(value)
    
    def test_specified_value_overrides_default(self):
        assert_equals(12, self.to_python('12'))
    
    def test_returns_default_for_empty_items(self):
        assert_equals(42, self.to_python(''))
        assert_equals(42, self.to_python(None))
    
    def test_can_return_unlimited_items(self):
        app_globals.settings['default_feed_results'] = ''
        assert_none(self.to_python(''))
        
        app_globals.settings['default_feed_results'] = '-1'
        assert_none(self.to_python(''))
    
    def test_ignores_missing_setting(self):
        del app_globals.settings['default_feed_results']
        assert_equals(30, self.to_python(''))
    
    def test_returns_default_number_for_invalid_input(self):
        assert_equals(42, self.to_python('invalid'))
        assert_equals(42, self.to_python(-1))
    
    def test_returns_default_for_missing_items(self):
        schema = Schema()
        schema.add_field('limit', self.validator)
        assert_equals(dict(limit=42), schema.to_python({}))



def suite():
    import unittest
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(LimitFeedItemsValidatorTest))
    return suite

