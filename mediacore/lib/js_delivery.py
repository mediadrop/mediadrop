# -*- coding: utf-8 -*-
# This file is a part of MediaDrop (http://www.mediadrop.net),
# Copyright 2009-2013 MediaDrop contributors
# For the exact contribution history, see the git revision log.
# The source code in this file is is dual licensed under the MIT license or
# the GPLv3 or (at your option) any later version.
# See LICENSE.txt in the main project directory, for more information.

from decimal import Decimal

import simplejson
from simplejson.encoder import JSONEncoderForHTML
from sqlalchemy.orm.properties import NoneType

__all__ = ['InlineJS', 'Script', 'Scripts']


class Script(object):
    def __init__(self, url, async=False, key=None):
        self.url = url
        self.async = async
        self.key = key
    
    def render(self):
        async = self.async and ' async="async"' or ''
        return '<script src="%s"%s type="text/javascript"></script>' % (self.url, async)
    
    def __unicode__(self):
        return self.render()
    
    def __repr__(self):
        return 'Script(%r, async=%r, key=%r)' % (self.url, self.async, self.key)
    
    def __eq__(self, other):
        # please note that two Script instances are considered equal when they
        # point to the same URL. The async attribute is not checked, let's not
        # include the same source code twice.
        if not hasattr(other, 'url'):
            return False
        return self.url == other.url
    
    def __ne__(self, other):
        return not (self == other)


class InlineJS(object):
    def __init__(self, code, key=None, params=None):
        self.code = code
        self.key = key
        self.params = params
    
    def as_safe_json(self, s):
        return simplejson.dumps(s, cls=JSONEncoderForHTML)
    
    def _escaped_parameters(self, params):
        escaped_params = dict()
        for key, value in params.items():
            if isinstance(value, (bool, NoneType)):
                # this condition must come first because "1 == True" in Python
                # but "1 !== true" in JavaScript and the "int" check below
                # would pass True unmodified
                escaped_params[key] = self.as_safe_json(value)
            elif isinstance(value, (int, long, float)):
                # use these numeric values directly as format string
                # parameters - they are mapped to JS types perfectly and don't
                # need any escaping.
                escaped_params[key] = value
            elif isinstance(value, (basestring, dict, tuple, list, Decimal)):
                escaped_params[key] = self.as_safe_json(value)
            else:
                klassname = value.__class__.__name__
                raise ValueError('unknown type %s' % klassname)
        return escaped_params
    
    def render(self):
        js = self.code
        if self.params is not None:
            js = self.code % self._escaped_parameters(self.params)
        return '<script type="text/javascript">%s</script>' % js
    
    def __unicode__(self):
        return self.render()
    
    def __repr__(self):
        return 'InlineJS(%r, key=%r)' % (self.code, self.key)
    
    def __eq__(self, other):
        # extremely simple equality check: two InlineJS instances are equal if 
        # the code is exactly the same! No trimming of whitespaces or any other
        # analysis is done.
        if not hasattr(other, 'render'):
            return False
        return self.render() == other.render()
    
    def __ne__(self, other):
        return not (self == other)


class SearchResult(object):
    def __init__(self, item, index):
        self.item = item
        self.index = index


class ResourcesCollection(object):
    def __init__(self, *args):
        self._resources = list(args)
    
    def replace_resource_with_key(self, new_resource):
        result = self._find_resource_with_key(new_resource.key)
        if result is None:
            raise AssertionError('No script with key %r' % new_resource.key)
        self._resources[result.index] = new_resource
    
    def render(self):
        markup = u''
        for resource in self._resources:
            markup = markup + resource.render()
        return markup
    
    def __len__(self):
        return len(self._resources)
    
    # --- internal api ---------------------------------------------------------
    
    def _get(self, resource):
        result = self._find_resource(resource)
        if result is not None:
            return result
        raise AssertionError('Resource %r not found' % resource)
    
    def _get_by_key(self, key):
        result = self._find_resource_with_key(key)
        if result is not None:
            return result
        raise AssertionError('No script with key %r' % key)
    
    def _find_resource(self, a_resource):
        for i, resource in enumerate(self._resources):
            if resource == a_resource:
                return SearchResult(resource, i)
        return None
    
    def _find_resource_with_key(self, key):
        for i, resource in enumerate(self._resources):
            if resource.key == key:
                return SearchResult(resource, i)
        return None


class Scripts(ResourcesCollection):
    def add(self, script):
        if script in self._resources:
            if not hasattr(script, 'async'):
                return
            # in case the same script is added twice and only one should be 
            # loaded asynchronously, use the non-async variant to be on the safe
            # side
            older_script = self._get(script).item
            older_script.async = older_script.async and script.async
            return
        self._resources.append(script)
    
    def add_all(self, *scripts):
        for script in scripts:
            self.add(script)
    
    # --- some interface polishing ---------------------------------------------
    @property
    def scripts(self):
        return self._resources
    
    def replace_script_with_key(self, script):
        self.replace_resource_with_key(script)

