# -*- coding: utf-8 -*-
# This file is a part of MediaCore CE, Copyright 2009-2012 MediaCore Inc.
# The source code contained in this file is licensed under the GPL.
# See LICENSE.txt in the main project directory, for more information.
#
# Copyright (c) 2012 Felix Schwarz (www.schwarz.eu)

from formencode.validators import Int
from pylons import request


__all__ = ['LimitFeedItemsValidator']

class LimitFeedItemsValidator(Int):
    min = 1
    
    def empty_value(self, value):
        return self.default_limit(request.settings)
    
    @property
    def if_missing(self):
        return self.default_limit(request.settings)
    
    @property
    def if_invalid(self):
        return self.default_limit(request.settings)
    
    def default_limit(self, settings):
        default_feed_results = settings.get('default_feed_results')
        if default_feed_results in ('', '-1'):
            return None
        elif default_feed_results is None:
            return 30
        return int(default_feed_results)
