# -*- coding: utf-8 -*-
# This file is a part of MediaDrop (http://www.mediadrop.net),
# Copyright 2009-2013 MediaDrop contributors
# For the exact contribution history, see the git revision log.
# The source code in this file is is dual licensed under the MIT license or
# the GPLv3 or (at your option) any later version.
# See LICENSE.txt in the main project directory, for more information.

from mediadrop.lib.js_delivery import ResourcesCollection

__all__ = ['StyleSheet', 'StyleSheets']

class StyleSheet(object):
    def __init__(self, url, key=None, media=None):
        self.url = url
        self.key = key
        self.media = media
    
    def render(self):
        template = '<link href="%s" rel="stylesheet" type="text/css"%s></link>'
        media = self.media and (' media="%s"' % self.media) or ''
        return template % (self.url, media)
    
    def __unicode__(self):
        return self.render()
    
    def __repr__(self):
        template = 'StyleSheet(%r, key=%r%s)'
        media = self.media and (', media=%r' % self.media) or ''
        return template % (self.url, self.key, media)
    
    def __eq__(self, other):
        if (not hasattr(other, 'url')) or (self.url != other.url):
            return False
        if (not hasattr(other, 'media')) or (self.media != other.media):
            return False
        return True
    
    def __ne__(self, other):
        return not (self == other)


class StyleSheets(ResourcesCollection):
    def add(self, stylesheet):
        if stylesheet in self._resources:
            return
        self._resources.append(stylesheet)
    
    def add_all(self, *stylesheets):
        for stylesheet in stylesheets:
            self.add(stylesheet)
    
    # --- some interface polishing ---------------------------------------------
    @property
    def stylesheets(self):
        return self._resources
    
    def replace_stylesheet_with_key(self, stylesheet):
        self.replace_resource_with_key(stylesheet)

