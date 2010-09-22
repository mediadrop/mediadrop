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
"""Helper functions

Consists of functions to typically be used within templates, but also
available to Controllers. This module is available to templates as 'h'.
"""
import hashlib
import os
import re
import shutil
import time
from datetime import datetime
from urllib import quote, unquote, urlencode
from urlparse import urlparse, urlsplit

import genshi.core
import pylons.templating
import pylons.test
import simplejson as json
import webob.exc

from BeautifulSoup import BeautifulSoup
from pylons import app_globals, config, request, response, url as pylons_url
from webhelpers import date, feedgenerator, html, number, misc, text, paginate, containers
from webhelpers.html import tags
from webhelpers.html.builder import literal
from webhelpers.html.converters import format_paragraphs

from mediacore.lib.compat import any
from mediacore.lib.htmlsanitizer import Cleaner, entities_to_unicode as decode_entities, encode_xhtml_entities as encode_entities
from mediacore.lib.thumbnails import thumb, thumb_url

imports = [
    'any', 'containers', 'date', 'decode_entities', 'encode_entities',
    'feedgenerator', 'format_paragraphs', 'html', 'literal', 'misc', 'number',
    'paginate', 'quote', 'tags', 'text', 'unquote', 'urlencode', 'urlparse',
    'config', # is this appropriate to export here?
    'thumb_url', # XXX: imported from  mediacore.lib.thumbnails, for template use.
    'thumb', # XXX: imported from  mediacore.lib.thumbnails, for template use.
]
defined = [
    'append_class_attr', 'clean_xhtml', 'delete_files', 'doc_link',
    'duration_from_seconds', 'duration_to_seconds', 'embeddable_player',
    'excerpt_xhtml', 'excess_whitespace', 'filter_library_controls',
    'get_featured_category', 'gravatar_from_email', 'is_admin', 'js',
    'line_break_xhtml', 'list_acceptable_xhtml',
    'pick_any_media_file', 'pick_podcast_media_file',
    'pretty_file_size', 'redirect',
    'store_transient_message', 'strip_xhtml', 'truncate', 'truncate_xhtml',
    'url', 'url_for', 'wrap_long_words',
]
__all__ = imports + defined

def url(*args, **kwargs):
    """Compose a URL with :func:`pylons.url`, all arguments are passed."""
    return _generate_url(pylons_url, *args, **kwargs)

def url_for(*args, **kwargs):
    """Compose a URL :func:`pylons.url.current`, all arguments are passed."""
    return _generate_url(pylons_url.current, *args, **kwargs)

# Mirror the behaviour you'd expect from pylons.url
url.current = url_for

def _generate_url(url_func, *args, **kwargs):
    """Generate a URL using the given callable."""
    # Convert unicode to str utf-8 for routes
    def to_utf8(value):
        if isinstance(value, unicode):
            return value.encode('utf-8')
        return value

    if args:
        args = [to_utf8(val) for val in args]
    if kwargs:
        kwargs = dict((key, to_utf8(val)) for key, val in kwargs.items())

    # TODO: Rework templates so that we can avoid using .current, and use named
    # routes, as described at http://routes.groovie.org/manual.html#generating-routes-based-on-the-current-url
    # NOTE: pylons.url is a StackedObjectProxy wrapping the routes.url method.
    url = url_func(*args, **kwargs)

    # If the proxy_prefix config directive is set up, then we need to make sure
    # that the SCRIPT_NAME is prepended to the URL. This SCRIPT_NAME prepending
    # is necessary for mod_proxy'd deployments, and for FastCGI deployments.
    # XXX: Leaking abstraction below. This code is tied closely to Routes 1.12
    #      implementation of routes.util.URLGenerator.__call__()
    # If the arguments given didn't describe a raw URL, then Routes 1.12 didn't
    # prepend the SCRIPT_NAME automatically--we'll need to feed the new URL
    # back to the routing method to prepend the SCRIPT_NAME.
    prefix = config.get('proxy_prefix', None)
    if prefix:
        if args:
            named_route = config['routes.map']._routenames.get(args[0])
            protocol = urlparse(args[0]).scheme
            static = not named_route and (args[0][0]=='/' or protocol)
        else:
            static = False
            protocol = ''

        if not static:
            if kwargs.get('qualified', False):
                offset = len(urlparse(url).scheme+"://")
            else:
                offset = 0
            path_index = url.index('/', offset)
            url = url[:path_index] + prefix + url[path_index:]

    return url

js_sources = {
    'mootools_more': '/scripts/third-party/mootools-1.2.4.4-more-yui-compressed.js',
    'mootools_core': 'http://ajax.googleapis.com/ajax/libs/mootools/1.2.4/mootools-yui-compressed.js',
# Debugging values:
    'mootools_more': '/scripts/third-party/mootools-1.2.4.4-more.js',
    'mootools_core': '/scripts/third-party/mootools-1.2.4-core.js',
}
def js(source):
    if pylons.test.pylonsapp:
        return js_sources[source]
    else:
        return url_for(js_sources[source])


def redirect(*args, **kwargs):
    """Compose a URL using :func:`url_for` and raise a redirect.

    :raises: :class:`webob.exc.HTTPFound`
    """
    url = url_for(*args, **kwargs)
    found = webob.exc.HTTPFound(location=url)
    raise found.exception

def duration_from_seconds(total_sec, shortest=True):
    """Return the HH:MM:SS duration for a given number of seconds.

    Does not support durations longer than 24 hours.

    :param total_sec: Number of seconds to convert into hours, mins, sec
    :type total_sec: int
    :param shortest: If True, return the shortest possible timestamp.
        Defaults to True.
    :rtype: unicode
    :returns: String HH:MM:SS, omitting the hours if less than one.

    """
    if not total_sec:
        return u''
    total = time.gmtime(total_sec)
    if not shortest:
        return u'%02d:%02d:%02d' % total[3:6]
    elif total.tm_hour > 0:
        return u'%d:%02d:%02d' % total[3:6]
    else:
        return u'%d:%02d' % total[4:6]

def duration_to_seconds(duration):
    """Return the number of seconds in a given HH:MM:SS.

    Does not support durations longer than 24 hours.

    :param duration: A HH:MM:SS or MM:SS formatted string
    :type duration: unicode
    :rtype: int
    :returns: seconds
    :raises ValueError: If the input doesn't matched the accepted formats

    """
    if not duration:
        return 0
    try:
        total = time.strptime(duration, '%H:%M:%S')
    except ValueError:
        total = time.strptime(duration, '%M:%S')
    return total.tm_hour * 60 * 60 + total.tm_min * 60 + total.tm_sec

def truncate(string, size, whole_word=True):
    """Truncate a plaintext string to roughly a given size (full words).

    :param string: plaintext
    :type string: unicode
    :param size: Max length
    :param whole_word: Whether to prefer truncating at the end of a word.
        Defaults to True.
    :rtype: unicode
    """
    return text.truncate(string, size, whole_word=whole_word)

# Configuration for HTML sanitization
blank_line = re.compile("\s*\n\s*\n\s*", re.M)
block_tags = 'p br pre blockquote div h1 h2 h3 h4 h5 h6 hr ul ol li form table tr td tbody thead'.split()
block_spaces = re.compile("\s*(</{0,1}(" + "|".join(block_tags) + ")>)\s*", re.M)
block_close = re.compile("(</(" + "|".join(block_tags) + ")>)", re.M)
valid_tags = dict.fromkeys('p i em strong b u a br pre abbr ol ul li sub sup ins del blockquote cite'.split())
valid_attrs = dict.fromkeys('href title'.split())
elem_map = {'b': 'strong', 'i': 'em'}
truncate_filters = ['strip_empty_tags']
cleaner_filters = [
        'add_nofollow', 'br_to_p', 'clean_whitespace', 'encode_xml_specials',
        'make_links', 'rename_tags', 'strip_attrs', 'strip_cdata',
        'strip_comments', 'strip_empty_tags', 'strip_schemes', 'strip_tags'
]
# Map all invalid block elements to be paragraphs.
for t in block_tags:
    if t not in valid_tags:
        elem_map[t] = 'p'
cleaner_settings = dict(
    convert_entities = BeautifulSoup.ALL_ENTITIES,
    valid_tags = valid_tags,
    valid_attrs = valid_attrs,
    elem_map = elem_map,
    filters = cleaner_filters
)

def clean_xhtml(string, p_wrap=True, _cleaner_settings=None):
    """Convert the given plain text or HTML into valid XHTML.

    If there is no markup in the string, apply paragraph formatting.

    :param string: XHTML input string
    :type string: unicode
    :param p_wrap: Wrap the output in <p></p> tags?
    :type p_wrap: bool
    :param _cleaner_settings: Constructor kwargs for
        :class:`mediacore.lib.htmlsanitizer.Cleaner`
    :type _cleaner_settings: dict
    :returns: XHTML
    :rtype: unicode
    """
    if not string or not string.strip():
        # If the string is none, or empty, or whitespace
        return u""

    if _cleaner_settings is None:
        _cleaner_settings = cleaner_settings

    # remove carriage return chars; FIXME: is this necessary?
    string = string.replace(u"\r", u"")

    # remove non-breaking-space characters. FIXME: is this necessary?
    string = string.replace(u"\xa0", u" ")
    string = string.replace(u"&nbsp;", u" ")

    # replace all blank lines with <br> tags
    string = blank_line.sub(u"<br/>", string)

    # initialize and run the cleaner
    string = Cleaner(string, **_cleaner_settings)()
    # FIXME: It's possible that the rename_tags operation creates
    # some invalid nesting. e.g.
    # >>> c = Cleaner("", "rename_tags", elem_map={'h2': 'p'})
    # >>> c('<p><h2>head</h2></p>')
    # u'<p><p>head</p></p>'
    # This is undesirable, so here we... just re-parse the markup.
    # But this ... could be pretty slow.
    cleaner = Cleaner(string, **_cleaner_settings)
    string = cleaner()

    # Wrap in a <p> tag when no tags are used, and there are no blank
    # lines to trigger automatic <p> creation
    # FIXME: This should trigger any time we don't have a wrapping block tag
    # FIXME: This doesn't wrap orphaned text when it follows a <p> tag, for ex
    if p_wrap \
        and len(cleaner.root.contents) == 1 \
        and isinstance(cleaner.root.contents[0], basestring):
        string = u"<p>%s</p>" % string.strip()

    # strip all whitespace from immediately before/after block-level elements
    string = block_spaces.sub(u"\\1", string)

    return string.strip()

def truncate_xhtml(string, size, _strip_xhtml=False, _decode_entities=False):
    """Truncate a XHTML string to roughly a given size (full words).

    :param string: XHTML
    :type string: unicode
    :param size: Max length
    :param _strip_xhtml: Flag to strip out all XHTML
    :param _decode_entities: Flag to convert XHTML entities to unicode chars
    :rtype: unicode
    """
    if not string:
        return u''

    if _strip_xhtml:
        # Insert whitespace after block elements.
        # So they are separated when we strip the xhtml.
        string = block_spaces.sub(u"\\1 ", string)
        string = strip_xhtml(string)

    string = decode_entities(string)

    if len(string) > size:
        string = text.truncate(string, length=size, whole_word=True)

        if _strip_xhtml:
            if not _decode_entities:
                # re-encode the entities, if we have to.
                string = encode_entities(string)
        else:
            if _decode_entities:
                string = Cleaner(string,
                                 *truncate_filters, **cleaner_settings)()
            else:
                # re-encode the entities, if we have to.
                string = Cleaner(string, 'encode_xml_specials',
                                 *truncate_filters, **cleaner_settings)()

    return string.strip()

def excerpt_xhtml(string, size, buffer=60):
    """Return an excerpt for the given string.

    Truncate to the given size iff we are removing more than the buffer size.

    :param string: A XHTML string
    :param size: The desired length
    :type size: int
    :param buffer: How much more than the desired length we can go to
        avoid truncating just a couple words etc.
    :type buffer: int
    :returns: XHTML

    """
    if not string:
        return u''
    new_str = decode_entities(string)
    if len(new_str) <= size + buffer:
        return string
    return truncate_xhtml(new_str, size)

def strip_xhtml(string, _decode_entities=False):
    """Strip out xhtml and optionally convert HTML entities to unicode.

    :rtype: unicode
    """
    if not string:
        return u''

    string = ''.join(BeautifulSoup(string).findAll(text=True))

    if _decode_entities:
        string = decode_entities(string)

    return string

def line_break_xhtml(string):
    """Add a linebreak after block-level tags are closed.

    :type string: unicode
    :rtype: unicode
    """
    if string:
        string = block_close.sub(u"\\1\n", string).rstrip()
    return string

html_entities = re.compile(r'&(\#x?[0-9a-f]{2,6}|[a-z]{2,10});')
long_words = re.compile(r'((\w|' + html_entities.pattern + '){5})([^\b])')

def wrap_long_words(string, _encode_entities=True):
    """Inject <wbr> periodically to let the browser wrap the string.

    The <wbr /> tag is widely deployed and included in HTML5,
    but it isn't XHTML-compliant. See this for more info:
    http://dev.w3.org/html5/spec/text-level-semantics.html#the-wbr-element

    :type string: unicode
    :rtype: literal
    """
    if _encode_entities:
        string = encode_entities(string)
    def inject_wbr(match):
        groups = match.groups()
        return u'%s<wbr />%s' % (groups[0], groups[-1])
    string = long_words.sub(inject_wbr, string)
    string = u'.<wbr />'.join(string.split('.'))
    return literal(string)

def list_acceptable_xhtml():
    return dict(
        tags = ", ".join(sorted(valid_tags)),
        attrs = ", ".join(sorted(valid_attrs)),
        map = ", ".join(["%s -> %s" % (t, elem_map[t]) for t in elem_map])
    )

def append_class_attr(attrs, class_name):
    """Append to the class for any input that Genshi's py:attrs understands.

    This is useful when using XIncludes and you want to append a class
    to the body tag, while still allowing all other tags to remain
    unchanged.

    For example::

        <body py:match="body" py:attrs="h.append_class_attr(select('@*'), 'extra_special')">

    :param attrs: A collection of attrs
    :type attrs: :class:`genshi.core.Stream`, :class:`genshi.core.Attrs`,
        ``list`` of 2-tuples, ``dict``
    :param class_name: The class name to append
    :type class_name: unicode
    :returns: All attrs
    :rtype: ``dict``

    """
    if isinstance(attrs, genshi.core.Stream):
        attrs = list(attrs)
        attrs = attrs and attrs[0] or []
    if not isinstance(attrs, dict):
        attrs = dict(attrs or ())
    attrs['class'] = unicode(attrs.get('class', '') + ' ' + class_name).strip()
    return attrs

excess_whitespace = re.compile('\s\s+', re.M)
spaces_between_tags = re.compile('>\s+<', re.M)

def embeddable_player(media):
    """Return a string of XHTML for embedding our player on other sites.

    All URLs include the domain (they're fully qualified).

    Since this returns a plain string, it is automatically escaped by Genshi
    when called in a template.

    :param media: The item to embed
    :type media: :class:`mediacore.model.media.Media` instance
    :returns: Unicode XHTML
    :rtype: :class:`webhelpers.html.builder.literal`

    """
    # FIXME: This doesn't do anything different than media_player, yet.
    from mediacore.lib.players import manager
    return manager().render(media)

def get_featured_category():
    from mediacore.model import Category
    feat_id = app_globals.settings['featured_category']
    if not feat_id:
        return None
    feat_id = int(feat_id)
    return Category.query.get(feat_id)

def filter_library_controls(query, show='latest'):
    from mediacore.model import Media
    if show == 'latest':
        query = query.order_by(Media.publish_on.desc())
    elif show == 'popular':
        query = query.order_by(Media.popularity_points.desc())
    elif show == 'featured':
        featured_cat = get_featured_category()
        if featured_cat:
            query = query.in_category(featured_cat)
    return query, show

def is_admin():
    """Return True if the logged in user is a part of the Admins group.

    This method will need to be replaced when we improve our user
    access controls.
    """
    groups = request.environ.get('repoze.who.identity', {}).get('groups', 0)
    return groups and any(group.lower() == 'admins' for group in groups)

def gravatar_from_email(email, size):
    """Return the URL for a gravatar image matching the povided email address.

    :param email: the email address
    :type email: string or unicode or None
    :param size: the width (or height) of the desired image
    :type size: int
    """
    if email is None:
        email = ''
    # Set your variables here
    gravatar_url = "http://www.gravatar.com/avatar/%s?size=%d" % \
        (hashlib.md5(email).hexdigest(), size)
    return gravatar_url

def pretty_file_size(size):
    """Return the given file size in the largest possible unit of bytes."""
    if not size:
        return u'-'
    for unit in ('B', 'KB', 'MB', 'GB', 'TB'):
        if size < 1024.0:
            return '%3.1f %s' % (size, unit)
        size /= 1024.0
    return '%3.1f %s' % (size, 'PB')

def delete_files(paths, subdir=None):
    """Move the given files to the 'deleted' folder, or just delete them.

    If the config contains a deleted_files_dir setting, then files are
    moved there. If that setting does not exist, or is empty, then the
    files will be deleted permanently instead.

    :param paths: File paths to delete. These files do not necessarily
        have to exist.
    :type paths: list
    :param subdir: A subdir within the configured deleted_files_dir to
        move the given files to. If this folder does not yet exist, it
        will be created.
    :type subdir: str or ``None``

    """
    deleted_dir = config.get('deleted_files_dir', None)
    if deleted_dir and subdir:
        deleted_dir = os.path.join(deleted_dir, subdir)
    if deleted_dir and not os.path.exists(deleted_dir):
        os.mkdir(deleted_dir)
    for path in paths:
        if path and os.path.exists(path):
            if deleted_dir:
                shutil.move(path, deleted_dir)
            else:
                os.remove(path)

def store_transient_message(cookie_name, text, time=None, path='/', **kwargs):
    """Store a JSON message dict in the named cookie.

    The cookie will expire at the end of the session, but should be
    explicitly deleted by whoever reads it.

    :param cookie_name: The cookie name for this message.
    :param text: Message text
    :param time: Optional time to report. Defaults to now.
    :param path: Optional cookie path
    :param kwargs: Passed into the JSON dict
    :returns: The message python dict
    :rtype: dict

    """
    time = datetime.now().strftime('%H:%M, %B %d, %Y')
    msg = kwargs
    msg['text'] = text
    msg['time'] = time or datetime.now().strftime('%H:%M, %B %d, %Y')
    new_data = quote(json.dumps(msg))
    response.set_cookie(cookie_name, new_data, path=path)
    return msg

def media_player(*args, **kwargs):
    """Render the media player for the given media.

    See :class:`mediacore.lib.players.AbstractPlayersManager`.
    """
    from mediacore.lib.players import manager
    return manager().render(*args, **kwargs)

def pick_podcast_media_file(media):
    """Return the best choice of files to play.

    XXX: This method uses the
         :ref:`~mediacore.lib.filetypes.pick_media_file_player` method and
         comes with the same caveats.

    :param media: A :class:`~mediacore.model.media.Media` instance.
    :returns: A :class:`~mediacore.model.media.MediaFile` object or None
    """
    from mediacore.lib.players import iTunesPlayer, manager
    uris = manager().sort_uris(media.get_uris())
    for i, plays in enumerate(iTunesPlayer.can_play(uris)):
        if plays:
            return uris[i]
    return None

def pick_any_media_file(media):
    """Return a file playable in at least one browser, with the current
    player_type setting, or None.

    XXX: This method uses the
         :ref:`~mediacore.lib.filetypes.pick_media_file_player` method and
         comes with the same caveats.

    :param media: A :class:`~mediacore.model.media.Media` instance.
    :returns: A :class:`~mediacore.model.media.MediaFile` object or None
    """
    from mediacore.lib.players import manager
    manager = manager()
    uris = manager.sort_uris(media.get_uris())
    for player in manager.players:
        for i, plays in enumerate(player.can_play(uris)):
            if plays:
                return uris[i]
    return None

def pick_uris(uris, **kwargs):
    """Return a subset of the given URIs whose attributes match the kwargs.

    This function attempts to simplify the somewhat unwieldly process of
    filtering a list of :class:`mediacore.lib.storage.StorageURI` instances
    for a specific type, protocol, container, etc::

        pick_uris(uris, scheme='rtmp', container='mp4', type='video')

    :type uris: iterable or :class:`~mediacore.model.media.Media` or
        :class:`~mediacore.model.media.MediaFile` instance
    :params uris: A collection of :class:`~mediacore.lib.storage.StorageURI`
        instances, including Media and MediaFile objects.
    :param \*\*kwargs: Required attribute values. These attributes can be
        on the `StorageURI` instance or, failing that, on the `StorageURI.file`
        instance within it.
    :rtype: list
    :returns: A subset of the input `uris`.

    """
    if not isinstance(uris, (list, tuple)):
        from mediacore.model.media import Media, MediaFile
        if isinstance(uris, (Media, MediaFile)):
            uris = uris.get_uris()
    if not uris or not kwargs:
        return uris
    return [uri
            for uri in uris
            if all(getattr(uri, k) == v for k, v in kwargs.iteritems())]

def pick_uri(uris, **kwargs):
    """Return the first URL that meets the given criteria.

    See: :func:`pick_uris`.

    :returns: A :class:`mediacore.lib.storage.StorageURI` instance or None.
    """
    uris = pick_uris(uris, **kwargs)
    if uris:
        return uris[0]
    return None

def download_uri(uris):
    """Pick out the best possible URI for downloading purposes.

    :returns: A :class:`mediacore.lib.storage.StorageURI` instance or None.
    """
    uris = pick_uris(uris, scheme='download')\
        or pick_uris(uris, scheme='http')
    uris.sort(key=lambda uri: uri.file.size, reverse=True)
    if uris:
        return uris[0]
    return None

def web_uri(uris):
    """Pick out the web link URI for viewing an embed in its original context.

    :returns: A :class:`mediacore.lib.storage.StorageURI` instance or None.
    """
    return pick_uri(uris, scheme='www')\
        or None

def best_link_uri(uris):
    """Pick out the best general purpose URI from those given.

    :returns: A :class:`mediacore.lib.storage.StorageURI` instance or None.
    """
    return pick_uri(uris, scheme='download')\
        or pick_uri(uris, scheme='http')\
        or pick_uri(uris, scheme='www')\
        or pick_uri(uris)\
        or None

def file_path(uris):
    """Pick out the local file path from the given list of URIs.

    Local file paths are passed around as urlencoded strings in
    :class:`mediacore.lib.storage.StorageURI`. The form is:

        file:///path/to/file

    :rtype: `str` or `unicode` or `None`
    :returns: Absolute /path/to/file
    """
    uris = pick_uris(uris, scheme='file')
    if uris:
        scheme, netloc, path, query, fragment = urlsplit(uris[0].file_uri)
        return path
    return None

def doc_link(page=None, anchor='', text='Help', **kwargs):
    """Return a link (anchor element) to the documentation on the project site.

    XXX: Target attribute is not XHTML compliant.
    """
    attrs = {
        'href': 'http://getmediacore.com/docs/user/%s.html#%s' % (page, anchor),
        'target': '_blank',
    }
    if kwargs:
        attrs.update(kwargs)
    attrs_string = ' '.join(['%s="%s"' % (key, attrs[key]) for key in attrs])
    out = '<a %s>%s</a>' % (attrs_string, text)
    return literal(out)
