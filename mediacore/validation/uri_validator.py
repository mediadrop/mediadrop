# -*- coding: utf-8 -*-
# This file is a part of MediaDrop (http://www.mediadrop.net),
# Copyright 2009-2013 MediaDrop contributors
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
        path = splitted_url[2] # '.path' in Python 2.5+
        # Python 2.4 does not fill netloc when parsing urls with unknown
        # schemes (e.g. 'rtmp://')
        netloc_given = (len(netloc) > 0) or (path.startswith('//') and path != '//')
        if (scheme == '') or not netloc_given:
            self.raise_error_bad_url(value, state)

