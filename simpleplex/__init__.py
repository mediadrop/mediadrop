import sys

__version__ = '0.7'

def debug(*args):
    """Print to stderr, for debuging"""
    print >> sys.stderr, "Simpleplex DEBUG", args
    return None

def ipython():
    """Launch an ipython shell where called before finishing the request.

    This only works with the Pylons paster server, and obviously ipython
    must be installed as well. Usage::

    simpleplex.ipython()()

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

# Monkey Patch Beautiful Soup
from BeautifulSoup import NavigableString as _NavigableString
@monkeypatch_method(_NavigableString)
def __eq__(self, other):
    """Monkey-patch inserted method.

    This patch is a temporary solution to the problem described here:
        http://bugs.launchpad.net/beautifulsoup/+bug/397997
    """
    if isinstance(other, _NavigableString):
        return other is self
    else:
        return unicode.__eq__(self, other)
