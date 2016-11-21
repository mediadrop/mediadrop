# encoding: utf-8
# This file is a part of MediaDrop (http://www.mediadrop.video),
# Copyright 2009-2014 MediaDrop contributors
# For the exact contribution history, see the git revision log.
# The source code in this file is is dual licensed under the MIT license or
# the GPLv3 or (at your option) any later version.
# See LICENSE.txt in the main project directory, for more information.

from __future__ import absolute_import

from decimal import Decimal

from ..filesize import format_filesize, human_readable_size
from mediadrop.lib.test.pythonic_testcase import *


class HumanReadableSizeTestCase(PythonicTestCase):
    def test_finds_highest_unit(self):
        assert_equals((Decimal(425), 'B'), human_readable_size(425))
        assert_equals((Decimal(12), 'KB'), human_readable_size(12*1024))
        assert_equals((Decimal(12), 'MB'), human_readable_size(12*1024**2))
        assert_equals((Decimal(12), 'GB'), human_readable_size(12*1024**3))
        assert_equals((Decimal(12), 'TB'), human_readable_size(12*1024**4))
        assert_equals((Decimal(10240), 'TB'), human_readable_size(10*1024**5))

    def test_finds_correct_units_for_negative_sizes(self):
        assert_equals((Decimal(-425), 'B'), human_readable_size(-425))
        assert_equals((Decimal(-12), 'KB'), human_readable_size(-12*1024))
        assert_equals((Decimal(-12), 'MB'), human_readable_size(-12*1024**2))
        assert_equals((Decimal(-12), 'GB'), human_readable_size(-12*1024**3))
        assert_equals((Decimal(-12), 'TB'), human_readable_size(-12*1024**4))
        assert_equals((Decimal(-10240), 'TB'), human_readable_size(-10*1024**5))


class FormatFilesizeTestCase(PythonicTestCase):
    def test_can_return_formatted_string_for_default_locale(self):
        assert_equals(u'12.8\xa0MB', format_filesize(12.8*1024**2))
        assert_equals(u'-10,240\xa0TB', format_filesize(-10*1024**5))

    def test_can_return_formatted_string_for_specified_locale(self):
        assert_equals(u'5\xa0KB', format_filesize(5*1024, locale='de'),
            message='do not render decimal places if not necessary')
        assert_equals(u'1,2\xa0MB', format_filesize(1.2*1024**2, locale='de'))
        assert_equals(u'12,9\xa0MB', format_filesize(12.854*1024**2, locale='de'),
            message='render at most one decimal digit')
        assert_equals(u'-10.240\xa0TB', format_filesize(-10*1024**5, locale='de'))

import unittest
def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(HumanReadableSizeTestCase))
    suite.addTest(unittest.makeSuite(FormatFilesizeTestCase))
    return suite

