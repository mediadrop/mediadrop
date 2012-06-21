# -*- coding: utf-8 -*-
#
# Copyright (c) 2012 Felix Schwarz <felix.schwarz@oss.schwarz.eu>
#
# This file may be used under the terms of the MIT license (see license text 
# below) or the GNU General Public License as published by the Free Software 
# Foundation, either version 3 of the License, or (at your option) any later 
# version.
# 
# The MIT License
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

__all__ = ['InlineJS', 'Script']


class Script(object):
    def __init__(self, url, async=False):
        self.url = url
        self.async = async
    
    def __unicode__(self):
        async = self.async and ' async="async"' or ''
        return '<script src="%s" %s type="text/javascript"></script>' % (self.url, async)

class InlineJS(object):
    def __init__(self, code):
        self.code = code
    
    def __unicode__(self):
        return '<script type="text/javascript">%s</script>' % self.code

