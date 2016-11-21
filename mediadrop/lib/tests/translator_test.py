# This file is a part of MediaDrop (http://www.mediadrop.video),
# Copyright 2009-2015 MediaDrop contributors
# For the exact contribution history, see the git revision log.
# The source code contained in this file is licensed under the GPLv3 or
# (at your option) any later version.
# See LICENSE.txt in the main project directory, for more information.

import os
import tempfile
import shutil

from babel.messages import Catalog
from babel.messages.mofile import write_mo

from mediadrop.lib.test import DBTestCase
from mediadrop.lib.test.pythonic_testcase import *
from mediadrop.lib.i18n import Translator


class TranslatorTest(DBTestCase):
    def setUp(self):
        super(TranslatorTest, self).setUp()
        self._tempdir = None
    
    def tearDown(self):
        if self._tempdir is not None:
            shutil.rmtree(self._tempdir)
        super(TranslatorTest, self).tearDown()
    
    def test_returns_input_for_unknown_domain(self):
        translator = Translator('de', {})
        assert_equals(u'foo', translator.gettext(u'foo', domain=u'unknown'))
    
    def _create_catalog(self, path_id, domain=u'foo', locale=u'de', **messages):
        i18n_dir = os.path.join(self._tempdir, path_id)
        path = os.path.join(i18n_dir, locale, 'LC_MESSAGES')
        os.makedirs(path)
        mo_filename = os.path.join(path, '%s.mo' % domain)
        assert_false(os.path.exists(mo_filename))
        
        catalog = Catalog(locale=locale, domain=domain, fuzzy=False)
        for message_id, translation in messages.items():
            catalog.add(message_id, translation)
        mo_fp = file(mo_filename, 'wb')
        write_mo(mo_fp, catalog)
        mo_fp.close()
        return i18n_dir
    
    def test_supports_multiple_locale_paths_for_single_domain(self):
        self._tempdir = tempfile.mkdtemp()
        first_path = self._create_catalog('first', something=u'foobar')
        second_path = self._create_catalog('second', something=u'baz')
        translator = Translator('de', {'foo': (first_path, second_path)})
        assert_equals('baz', translator.gettext('something', domain='foo'))


import unittest
def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TranslatorTest))
    return suite

