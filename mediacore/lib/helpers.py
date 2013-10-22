# This file is a part of MediaDrop (http://www.mediadrop.net),
# Copyright 2009-2013 MediaCore Inc., Felix Schwarz and other contributors.
# For the exact contribution history, see the git revision log.
# The source code contained in this file is licensed under the GPLv3 or
# (at your option) any later version.
# See LICENSE.txt in the main project directory, for more information.
"""Helper functions

Consists of functions to typically be used within templates, but also
available to Controllers. This module is available to templates as 'h'.
"""
import re
import simplejson
import time
import warnings

from datetime import datetime
from urllib import quote, unquote, urlencode
from urlparse import urlparse

from genshi.core import Stream
from paste.util import mimeparse
from pylons import app_globals, config, request, response, translator
from webhelpers import date, feedgenerator, html, number, misc, text, paginate, containers
from webhelpers.html import tags
from webhelpers.html.builder import literal
from webhelpers.html.converters import format_paragraphs

from mediacore.lib.auth import viewable_media
from mediacore.lib.compat import any, md5
from mediacore.lib.i18n import (N_, _, format_date, format_datetime, 
    format_decimal, format_time)
from mediacore.lib.players import (embed_player, embed_iframe, media_player,
    pick_any_media_file, pick_podcast_media_file)
from mediacore.lib.thumbnails import thumb, thumb_url
from mediacore.lib.uri import (best_link_uri, download_uri, file_path,
    pick_uri, pick_uris, web_uri)
from mediacore.lib.util import (current_url, delete_files, merge_dicts, 
    redirect, url, url_for, url_for_media)
from mediacore.lib.xhtml import (clean_xhtml, decode_entities, encode_entities,
    excerpt_xhtml, line_break_xhtml, list_acceptable_xhtml, strip_xhtml,
    truncate_xhtml)
from mediacore.plugin.events import (meta_description, meta_keywords,
    meta_robots_noindex, observes, page_title)

__all__ = [
    # Imports that should be exported:
    'any',
    'clean_xhtml',
    'current_url',
    'config', # is this appropriate to export here?
    'containers',
    'content_type_for_response',
    'date',
    'decode_entities',
    'encode_entities',
    'excerpt_xhtml',
    'feedgenerator',
    'format_date',
    'format_datetime',
    'format_decimal',
    'format_paragraphs',
    'format_time',
    'html',
    'line_break_xhtml',
    'list_acceptable_xhtml',
    'literal',
    'meta_description',
    'meta_keywords', # XXX: imported from mediacore.plugin.events
    'meta_robots_noindex',
    'misc',
    'number',
    'page_title', # XXX: imported from mediacore.plugin.events
    'paginate',
    'quote',
    'strip_xhtml',
    'tags',
    'text',
    'thumb', # XXX: imported from  mediacore.lib.thumbnails, for template use.
    'thumb_url', # XXX: imported from  mediacore.lib.thumbnails, for template use.
    'truncate_xhtml',
    'unquote',
    'url',
    'url_for',
    'url_for_media',
    'urlencode',
    'urlparse',
    'viewable_media',

    # Locally defined functions that should be exported:
    'append_class_attr',
    'best_translation',
    'can_edit',
    'delete_files',
    'doc_link',
    'duration_from_seconds',
    'duration_to_seconds',
    'filter_library_controls',
    'filter_vulgarity',
    'get_featured_category',
    'gravatar_from_email',
    'is_admin',
    'js',
    'mediacore_version',
    'pick_any_media_file',
    'pick_podcast_media_file',
    'pretty_file_size',
    'redirect',
    'store_transient_message',
    'truncate',
    'wrap_long_words',
]
__all__.sort()

js_sources = {
    'mootools_more': '/scripts/third-party/mootools-1.2.4.4-more-yui-compressed.js',
    'mootools_core': '/scripts/third-party/mootools-1.2.6-core-2013-01-16.min.js',
}
js_sources_debug = {
    'mootools_more': '/scripts/third-party/mootools-1.2.4.4-more.js',
    'mootools_core': '/scripts/third-party/mootools-1.2.6-core-2013-01-16.js',
}

def js(source):
    if config['debug'] and source in js_sources_debug:
        return url_for(js_sources_debug[source])
    return url_for(js_sources[source])

def mediacore_version():
    import mediacore
    return mediacore.__version__

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

def content_type_for_response(available_formats):
    content_type = mimeparse.best_match(
        available_formats,
        request.environ.get('HTTP_ACCEPT', '*/*')
    )
    # force a content-type: if the user agent did not specify any acceptable
    # content types (e.g. just 'text/html' like some bots) we still need to
    # set a content type, otherwise the WebOb will generate an exception
    # AttributeError: You cannot access Response.unicode_body unless charset
    # the only alternative to forcing a "bad" content type would be not to 
    # deliver any content at all - however most bots are just faulty and they
    # requested something like 'sitemap.xml'.
    return content_type or available_formats[0]

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

    XXX: There is an edge case where a function may be passed in as a result of using a lambda in a
         Tosca Widgets form definition to generate a dynamic container_attr value.
         In this rare case we are checking for a callable, and using that value.

    :param attrs: A collection of attrs
    :type attrs: :class:`genshi.core.Stream`, :class:`genshi.core.Attrs`, :function:
        ``list`` of 2-tuples, ``dict``
    :returns: All attrs
    :rtype: ``dict``
    """
    if isinstance(attrs, Stream):
        attrs = list(attrs)
        attrs = attrs and attrs[0] or []
    if callable(attrs):
        attrs = attrs()
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
        class_list.append(class_name)
        attrs['class'] = ' '.join(class_list)
    return attrs

spaces_between_tags = re.compile('>\s+<', re.M)

def get_featured_category():
    from mediacore.model import Category
    feat_id = request.settings['featured_category']
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

def has_permission(permission_name):
    """Return True if the logged in user has the given permission.

    This always returns false if the given user is not logged in."""
    return request.perm.contains_permission(permission_name)

def is_admin():
    """Return True if the logged in user has the "admin" permission.

    For a default install a user has the "admin" permission if he is a member
    of the "admins" group.

    :returns: Whether or not the current user has "admin" permission.
    :rtype: bool
    """
    return has_permission(u'admin')

def can_edit(item=None):
    """Return True if the logged in user has the "edit" permission.

    For a default install this is true for all members of the "admins" group.

    :param item: unused parameter (deprecated)
    :type item: unimplemented

    :returns: Whether or not the current user has "edit" permission.
    :rtype: bool
    """
    if item is not None:
        warnings.warn(u'"item" parameter for can_edit() is deprecated', 
          DeprecationWarning, stacklevel=2)
    return has_permission(u'edit')

def gravatar_from_email(email, size):
    """Return the URL for a gravatar image matching the provided email address.

    :param email: the email address
    :type email: string or unicode or None
    :param size: the width (or height) of the desired image
    :type size: int
    """
    if email is None:
        email = ''
    # Set your variables here
    gravatar_url = "http://www.gravatar.com/avatar/%s?size=%d" % \
        (md5(email).hexdigest(), size)
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
    new_data = quote(simplejson.dumps(msg))
    response.set_cookie(cookie_name, new_data, path=path)
    return msg

def doc_link(page=None, anchor='', text=N_('Help'), **kwargs):
    """Return a link (anchor element) to the documentation on the project site.

    XXX: Target attribute is not XHTML compliant.
    """
    attrs = {
        'href': 'http://mediadrop.net/docs/user/%s.html#%s' % (page, anchor),
        'target': '_blank',
    }
    if kwargs:
        attrs.update(kwargs)
    attrs_string = ' '.join(['%s="%s"' % (key, attrs[key]) for key in attrs])
    out = '<a %s>%s</a>' % (attrs_string, _(text))
    return literal(out)

@observes(page_title)
def default_page_title(default=None, **kwargs):
    settings = request.settings
    title_order = settings.get('general_site_title_display_order', None)
    site_name = settings.get('general_site_name', default)
    if not default:
        return site_name
    if not title_order:
        return '%s | %s' % (default, site_name)
    elif title_order.lower() == 'append':
        return '%s | %s' % (default, site_name)
    else:
        return '%s | %s' % (site_name, default)

@observes(meta_description)
def default_media_meta_description(default=None, media=None, **kwargs):
    if media and media != 'all' and media.description_plain:
        return truncate(media.description_plain, 249)
    return None

@observes(meta_keywords)
def default_media_meta_keywords(default=None, media=None, **kwargs):
    if media and media != 'all' and media.tags:
        return ', '.join(tag.name for tag in media.tags[:15])
    return None

def filter_vulgarity(text):
    """Return a sanitized version of the given string.

    Words are defined in the Comments settings and are
    replaced with \*'s representing the length of the filtered word.

    :param text: The string to be filtered.
    :type text: str

    :returns: The filtered string.
    :rtype: str

    """
    vulgar_words = request.settings.get('vulgarity_filtered_words', None)
    if vulgar_words:
        words = (word.strip() for word in vulgar_words.split(','))
        word_pattern = '|'.join(re.escape(word) for word in words if word)
        word_expr = re.compile(word_pattern, re.IGNORECASE)
        def word_replacer(matchobj):
            word = matchobj.group(0)
            return '*' * len(word)
        text = word_expr.sub(word_replacer, text)
    return text

def best_translation(a, b):
    """Return the best translation given a preferred and a fallback string.

    If we have a translation for our preferred string 'a' or if we are using
    English, return 'a'. Otherwise, return a translation for the fallback string 'b'.

    :param a: The preferred string to translate.
    :param b: The fallback string to translate.
    :returns: The best translation
    :rtype: string
    """
    translated_a = _(a)
    if a != translated_a or translator.locale.language == 'en':
        return translated_a
    else:
        return _(b)
