# This file is a part of MediaCore, Copyright 2009 Simple Station Inc.
#
# MediaCore is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# MediaCore is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import sys
from types import NoneType

# Module description following the guidelines at:
# http://bayes.colorado.edu/PythonGuidelines.html#module_formatting
__version__ = '0.8.2'
__status__ = 'Production'
__copyright__ = 'Copyright 2009-2010, Simple Station Inc.'
__license__ = 'GPLv3'
__email__ = 'info@simplestation.com'
__maintainer__ = 'http://getmediacore.com/'
__all__ = ['__version__', 'debug', 'ipython']

USER_AGENT = 'MediaCore/%s' % __version__

def debug(*args):
    """Print to stderr, for debuging"""
    print >> sys.stderr, "MediaCore DEBUG", args
    return None

def ipython():
    """Launch an ipython shell where called before finishing the request.

    This only works with the Pylons paster server, and obviously ipython
    must be installed as well. Usage::

        mediacore.ipython()()

    """
    from IPython.Shell import IPShellEmbed
    args = ['-pdb', '-pi1', 'In <\\#>: ', '-pi2', '   .\\D.: ',
            '-po', 'Out<\\#>: ', '-nosep']
    return IPShellEmbed(
        args,
        banner='Entering IPython.  Press Ctrl-D to exit.',
        exit_msg='Leaving Interpreter, back to Pylons.'
    )

def monkeypatch_method(cls):
    """MonkeyPatching decorator

    Described by Guido van Rossum, here:
        http://mail.python.org/pipermail/python-dev/2008-January/076194.html
    """
    def decorator(func):
        setattr(cls, func.__name__, func)
        return func
    return decorator

try:
    # Monkey Patch our StaticURLParser for Paste-1.7.4
    from paste.urlparser import StaticURLParser
    @monkeypatch_method(StaticURLParser)
    def add_slash(self, environ, start_response):
        """Monkey-patch overridden method.

        MediaCore doesn't use any public directory listings, or index.html
        files, so there's no reason to issue a redirect to normalize folder
        requests to have a trailing slash, as all of these URLs will 404
        either way.

        This also avoids useless redirects for routes that have the same name
        as a folder in the ./public directory, such as requests for "/admin".
        """
        environ['PATH_INFO'] = '/'
        sup = self.__class__(
            self.directory,
            root_directory=self.root_directory,
            cache_max_age=self.cache_max_age
        )
        return sup(environ, start_response)

    # Monkey Patch Beautiful Soup
    from BeautifulSoup import NavigableString
    @monkeypatch_method(NavigableString)
    def __eq__(self, other):
        """Monkey-patch inserted method.

        This patch is a temporary solution to the problem described here:
            http://bugs.launchpad.net/beautifulsoup/+bug/397997
        """
        if other is None:
            return False
        elif isinstance(other, NavigableString):
            return other is self
        else:
            return unicode(self) == unicode(other)
except ImportError:
    # When setup.py install is called, these monkeypatches will fail.
    # For now we'll just silently allow this to proceed.
    pass
