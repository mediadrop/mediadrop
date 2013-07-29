# This file is a part of MediaCore CE (http://www.mediacorecommunity.org),
# Copyright 2009-2013 MediaCore Inc., Felix Schwarz and other contributors.
# For the exact contribution history, see the git revision log.
# The source code contained in this file is licensed under the GPLv3 or
# (at your option) any later version.
# See LICENSE.txt in the main project directory, for more information.

import sys

# Module description following the guidelines at:
# http://bayes.colorado.edu/PythonGuidelines.html#module_formatting
__version__ = '0.10.2dev'
__status__ = 'Beta'
__copyright__ = 'Copyright 2009-2013, MediaCore Inc., Felix Schwarz and other contributors.'
__license__ = 'GPLv3'
__email__ = 'info@mediacore.com'
__maintainer__ = 'http://mediacorecommunity.org/'
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

        from mediacore import ipython
        ipython()()

    """
    import IPython
    return IPython.embed

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

    # Disable the webob.request.AdhocAttrMixin.
    # We want to be able to set and get attributes very quickly, and they
    # do not need to be persisted between new request instances.
    from pylons.controllers.util import Request
    from webob.request import BaseRequest
    Request.__setattr__ = BaseRequest.__setattr__
    Request.__getattr__ = BaseRequest.__getattribute__
    Request.__delattr__ = BaseRequest.__delattr__
    try:
        Request._setattr_stacklevel = BaseRequest._setattr_stacklevel
    except AttributeError:
        # Don't fail if we've been running v0.9.0 and thus haven't
        # updated to Web0b 1.0.7 yet
        pass
except ImportError:
    # When setup.py install is called, these monkeypatches will fail.
    # For now we'll just silently allow this to proceed.
    pass
