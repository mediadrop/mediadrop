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
from BeautifulSoup import NavigableString
@monkeypatch_method(NavigableString)
def __eq__(self, other):
    """Monkey-patch inserted method.

    This patch is a temporary solution to the problem described here:
        http://bugs.launchpad.net/beautifulsoup/+bug/397997
    """
    if isinstance(other, NavigableString):
        return other is self
    else:
        return unicode.__eq__(self, other)
del NavigableString
