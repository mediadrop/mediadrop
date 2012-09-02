# -*- coding: utf-8 -*-
# This file is a part of MediaCore CE, Copyright 2009-2012 MediaCore Inc.
# The source code in this file is dual licensed under the MIT license or the 
# GPL version 3 or (at your option) any later version.
# See LICENSE.txt in the main project directory, for more information.
#
# Copyright (c) 2012 Felix Schwarz (www.schwarz.eu)

__all__ = ['InlineJS', 'Script', 'Scripts']


class Script(object):
    def __init__(self, url, async=False, key=None):
        self.url = url
        self.async = async
        self.key = key
    
    def __unicode__(self):
        async = self.async and ' async="async"' or ''
        return '<script src="%s"%s type="text/javascript"></script>' % (self.url, async)
    
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
    def __init__(self, code, key=None):
        self.code = code
        self.key = key
    
    def __unicode__(self):
        return '<script type="text/javascript">%s</script>' % self.code
    
    def __repr__(self):
        return 'InlineJS(%r, key=%r)' % (self.code, self.key)
    
    def __eq__(self, other):
        # extremely simple equality check: two InlineJS instances are equal if 
        # the code is exactly the same! No trimming of whitespaces or any other
        # analysis is done.
        if not hasattr(other, 'code'):
            return False
        return self.code == other.code
    
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
            markup = markup + unicode(resource)
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
    
    # --- some interface polishing ---------------------------------------------
    @property
    def scripts(self):
        return self._resources
    
    def replace_script_with_key(self, script):
        self.replace_resource_with_key(script)

