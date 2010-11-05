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
from urlparse import urlparse

import genshi.core
import pylons.templating
import pylons.test
import simplejson as json
import webob.exc

from pylons import app_globals, config, request, response
from webhelpers import date, feedgenerator, html, number, misc, text, paginate, containers
from webhelpers.html import tags
from webhelpers.html.builder import literal
from webhelpers.html.converters import format_paragraphs

from mediacore.lib.compat import any
from mediacore.lib.players import (embed_player, embed_iframe, media_player,
    pick_any_media_file, pick_podcast_media_file)
from mediacore.lib.thumbnails import thumb, thumb_url
from mediacore.lib.uri import (best_link_uri, download_uri, file_path,
    pick_uri, pick_uris, web_uri)
from mediacore.lib.util import merge_dicts, redirect, url, url_for
from mediacore.lib.xhtml import (clean_xhtml, decode_entities, encode_entities,
    excerpt_xhtml, line_break_xhtml, list_acceptable_xhtml, strip_xhtml,
    truncate_xhtml)

imports = [
    'any', 'containers', 'clean_xhtml', 'date', 'decode_entities',
    'encode_entities', 'excerpt_xhtml', 'feedgenerator', 'format_paragraphs',
    'html', 'line_break_xhtml', 'list_acceptable_xhtml', 'literal', 'misc',
    'number', 'paginate', 'quote', 'strip_xhtml', 'tags', 'text',
    'truncate_xhtml', 'unquote', 'urlencode', 'urlparse', 'url', 'url_for',
    'config', # is this appropriate to export here?
    'thumb_url', # XXX: imported from  mediacore.lib.thumbnails, for template use.
    'thumb', # XXX: imported from  mediacore.lib.thumbnails, for template use.
]

defined = [
    'append_class_attr', 'delete_files', 'doc_link',
    'duration_from_seconds', 'duration_to_seconds',
    'excess_whitespace', 'filter_library_controls',
    'get_featured_category', 'gravatar_from_email', 'is_admin', 'js',
    'pick_any_media_file', 'pick_podcast_media_file',
    'pretty_file_size', 'redirect',
    'store_transient_message', 'truncate',
    'wrap_long_words',
]
__all__ = imports + defined

js_sources = {
    'mootools_more': '/scripts/third-party/mootools-1.2.4.4-more-yui-compressed.js',
    'mootools_core': 'http://ajax.googleapis.com/ajax/libs/mootools/1.2.5/mootools-yui-compressed.js',
}
js_sources_debug = {
    'mootools_more': '/scripts/third-party/mootools-1.2.4.4-more.js',
    'mootools_core': '/scripts/third-party/mootools-1.2.5-core.js',
}

def js(source):
    if config['debug'] and source in js_sources_debug:
        return url_for(js_sources_debug[source])
    return url_for(js_sources[source])

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

def attrs_to_dict(attrs):
    """Return a dict for any input that Genshi's py:attrs understands.

    For example::

        <link py:match="link" py:if="h.attrs_to_dict(select('@*'))['rel'] == 'alternate'">

    :param attrs: A collection of attrs
    :type attrs: :class:`genshi.core.Stream`, :class:`genshi.core.Attrs`,
        ``list`` of 2-tuples, ``dict``
    :returns: All attrs
    :rtype: ``dict``
    """
    if isinstance(attrs, genshi.core.Stream):
        attrs = list(attrs)
        attrs = attrs and attrs[0] or []
    if not isinstance(attrs, dict):
        attrs = dict(attrs or ())
    return attrs

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
    attrs = attrs_to_dict(attrs)
    classes = attrs.get('class', None)
    if not classes:
        attrs['class'] = class_name
        return attrs
    class_list = classes.split(' ')
    if class_name not in class_list:
        classes.append(classes)
        attrs['class'] = ' '.join(classes)
    return attrs

spaces_between_tags = re.compile('>\s+<', re.M)

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
    ident = request.environ.get('repoze.who.identity', {})
    groups = ident.get('groups', 0)
    return groups and any(group.lower() == 'admins' for group in groups)

def can_edit(item):
    """Return True if the logged in user is a part of the Admins group.

    NOTE: The item argument is provided for future use only.
    """
    ident = request.environ.get('repoze.who.identity', {})
    perms = ident.get('permissions', 0)
    return perms and any(perm.lower() == 'edit' for perm in perms)

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
    size = float(size)
    for unit in ('B', 'KB', 'MB', 'GB', 'TB'):
        if size < 1024.0:
            return '%3.1f %s' % (size, unit)
        size /= 1024.0
    return '%3.1f %s' % (size, 'PB')

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
