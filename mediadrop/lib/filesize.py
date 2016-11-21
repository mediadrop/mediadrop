# encoding: utf-8
# This file is a part of MediaDrop (http://www.mediadrop.video),
# Copyright 2009-2014 MediaDrop contributors
# For the exact contribution history, see the git revision log.
# The source code in this file is is dual licensed under the MIT license or
# the GPLv3 or (at your option) any later version.
# See LICENSE.txt in the main project directory, for more information.

from __future__ import division

from decimal import Decimal

from babel import Locale
from babel.numbers import format_decimal


__all__ = ['format_filesize', 'human_readable_size']

# -----------------------------------------------------------------------------
# Code initially from StackOverflow but modified by Felix Schwarz so the
# formatting aspect is separated from finding the right unit. Also it uses
# Python's Decimal instead of floats
# http://stackoverflow.com/a/1094933/138526
def human_readable_size(value):
    if not isinstance(value, Decimal):
        value = Decimal(str(value))
    for unit in ('B','KB','MB','GB'):
        if value < 1024 and value > -1024:
            return (value, unit)
        value = value / 1024
    return (value, 'TB')
# -----------------------------------------------------------------------------

def format_filesize(size, locale='en'):
    locale = Locale.parse(locale)
    value, unit = human_readable_size(size)
    return format_decimal(value, format=u'#,##0.#', locale=locale) + u'\xa0' + unit

