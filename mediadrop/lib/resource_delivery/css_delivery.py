# -*- coding: utf-8 -*-
# This file is a part of MediaDrop (https://www.mediadrop.video),
# Copyright 2009-2018 MediaDrop contributors
# For the exact contribution history, see the git revision log.
# The source code in this file is dual licensed under the MIT license or
# the GPLv3 or (at your option) any later version.
# See LICENSE.txt in the main project directory, for more information.

from .js_delivery import ResourcesCollection


__all__ = ['StyleSheet', 'StyleSheets', 'Stylesheet', 'Stylesheets']

class Stylesheet(object):
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
        template = 'Stylesheet(%r, key=%r%s)'
        media = self.media and (', media=%r' % self.media) or ''
        return template % (self.url, self.key, media)

    def __eq__(self, other):
        for attr_name in ('key', 'url', 'media'):
            if not hasattr(other, attr_name):
                return False
        if (self.key is not None) and (self.key == other.key) and (self.media == other.media):
            return True
        if (self.url == other.url) and (self.media == other.media):
            return True
        return False

    def __ne__(self, other):
        return not (self == other)


class Stylesheets(ResourcesCollection):
    def add(self, stylesheet):
        # ideally we should also merge the media values
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

# backwards compatibility
StyleSheet = Stylesheet
StyleSheets = Stylesheets

