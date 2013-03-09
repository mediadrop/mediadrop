# -*- coding: utf-8 -*-
# This file is a part of MediaCore CE (http://www.mediacorecommunity.org),
# Copyright 2009-2013 MediaCore Inc., Felix Schwarz and other contributors.
# For the exact contribution history, see the git revision log.
# The source code contained in this file is licensed under the GPLv3 or
# (at your option) any later version.
# See LICENSE.txt in the main project directory, for more information.

from urlparse import urlsplit

from formencode.validators import UnicodeString
from formencode.api import Invalid

from mediacore.lib.i18n import _


__all__ = ['URIValidator']

class URIValidator(UnicodeString):
    
    messages = {
        'bad_url': u'Unknown URL',
    }
    
    def raise_error_bad_url(self, value, state):
        msg = _('That is not a valid URL.')
        raise Invalid(msg, value, state)
    
    def validate_python(self, value, state):
        try:
            splitted_url = urlsplit(value)
        except:
            self.raise_error_bad_url(value, state)
        scheme = splitted_url[0] # '.scheme' in Python 2.5+
        netloc = splitted_url[1] # '.netloc' in Python 2.5+
        if (scheme == '') or (netloc == ''):
            self.raise_error_bad_url(value, state)

