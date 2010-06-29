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
import datetime as dt
import hashlib
import math
import os
import re
import shutil
import time
from PIL import Image
from copy import copy
from datetime import datetime
from urllib import urlencode, quote, unquote
from urlparse import urlparse

import genshi.core
import pylons.templating
import simplejson as json
import webob.exc

from BeautifulSoup import BeautifulSoup
from paste.util import mimeparse
from pylons import app_globals, config, request, response, url as pylons_url
from webhelpers import date, feedgenerator, html, number, misc, text, paginate, containers
from webhelpers.html import tags
from webhelpers.html.builder import literal
from webhelpers.html.converters import format_paragraphs

from mediacore.lib.compat import any
from mediacore.lib.htmlsanitizer import Cleaner, entities_to_unicode as decode_entities, encode_xhtml_entities as encode_entities
from mediacore.lib.filetypes import AUDIO, AUDIO_DESC, CAPTIONS, VIDEO, accepted_extensions, pick_media_file_player

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

def redirect(*args, **kwargs):
    """Compose a URL using :func:`url_for` and raise a redirect.

    :raises: :class:`webob.exc.HTTPFound`
    """
    url = url_for(*args, **kwargs)
    found = webob.exc.HTTPFound(location=url)
    raise found.exception

def duration_from_seconds(total_sec):
    """Return the HH:MM:SS duration for a given number of seconds.

    Does not support durations longer than 24 hours.

    :param total_sec: Number of seconds to convert into hours, mins, sec
    :type total_sec: int
    :rtype: unicode
    :returns: String HH:MM:SS, omitting the hours if less than one.

    """
    if not total_sec:
        return u''
    total = time.gmtime(total_sec)
    if total.tm_hour > 0:
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

    :param p_wrap: Wrap the output in <p></p> tags?
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

def list_accepted_extensions():
    """Return the extensions allowed for upload for printing.

    :returns: Comma separated extensions
    :rtype: unicode
    """
    e = accepted_extensions()
    if len(e) > 1:
        e[-1] = 'and ' + e[-1]
    return ', '.join(e)

def _normalize_thumb_item(item):
    """Pass back the image subdir and id when given a media or podcast."""
    try:
        return item._thumb_dir, item.id or 'new'
    except AttributeError:
        return item

def thumb_path(item, size, exists=False, ext='jpg'):
    """Get the thumbnail path for the given item and size.

    :param item: A 2-tuple with a subdir name and an ID. If given a
        ORM mapped class with _thumb_dir and id attributes, the info
        can be extracted automatically.
    :type item: ``tuple`` or mapped class instance
    :param size: Size key to display, see ``thumb_sizes`` in
        :mod:`mediacore.config.app_config`
    :type size: str
    :param exists: If enabled, checks to see if the file actually exists.
        If it doesn't exist, ``None`` is returned.
    :type exists: bool
    :param ext: The extension to use, defaults to jpg.
    :type ext: str
    :returns: The absolute system path or ``None``.
    :rtype: str

    """
    if not item:
        return None

    image_dir, item_id = _normalize_thumb_item(item)
    image = '%s/%s%s.%s' % (image_dir, item_id, size, ext)
    image_path = os.path.join(config['image_dir'], image)

    if exists and not os.path.isfile(image_path):
        return None
    return image_path

def thumb_paths(item, **kwargs):
    """Return a list of paths to all sizes of thumbs for a given item.

    :param item: A 2-tuple with a subdir name and an ID. If given a
        ORM mapped class with _thumb_dir and id attributes, the info
        can be extracted automatically.
    :type item: ``tuple`` or mapped class instance
    :returns: thumb sizes and their paths
    :rtype: ``dict``

    """
    image_dir, item_id = _normalize_thumb_item(item)
    return dict((key, thumb_path(item, key, **kwargs))
                for key in config['thumb_sizes'][image_dir].iterkeys())

def thumb_url(item, size, qualified=False, exists=False):
    """Get the thumbnail url for the given item and size.

    :param item: A 2-tuple with a subdir name and an ID. If given a
        ORM mapped class with _thumb_dir and id attributes, the info
        can be extracted automatically.
    :type item: ``tuple`` or mapped class instance
    :param size: Size key to display, see ``thumb_sizes`` in
        :mod:`mediacore.config.app_config`
    :type size: str
    :param qualified: If ``True`` return the full URL including the domain.
    :type qualified: bool
    :param exists: If enabled, checks to see if the file actually exists.
        If it doesn't exist, ``None`` is returned.
    :type exists: bool
    :returns: The relative or absolute URL.
    :rtype: str

    """
    if not item:
        return None

    image_dir, item_id = _normalize_thumb_item(item)
    image = '%s/%s%s.jpg' % (image_dir, item_id, size)

    if exists and not os.path.isfile(os.path.join(config['image_dir'], image)):
        return None
    return url_for('/images/%s' % image, qualified=qualified)

class ThumbDict(dict):
    """Dict wrapper with convenient attribute access"""

    def __init__(self, url, dimensions):
        self['url'] = url
        self['x'], self['y'] = dimensions

    def __getattr__(self, name):
        return self[name]

def thumb(item, size, qualified=False, exists=False):
    """Get the thumbnail url & dimensions for the given item and size.

    :param item: A 2-tuple with a subdir name and an ID. If given a
        ORM mapped class with _thumb_dir and id attributes, the info
        can be extracted automatically.
    :type item: ``tuple`` or mapped class instance
    :param size: Size key to display, see ``thumb_sizes`` in
        :mod:`mediacore.config.app_config`
    :type size: str
    :param qualified: If ``True`` return the full URL including the domain.
    :type qualified: bool
    :param exists: If enabled, checks to see if the file actually exists.
        If it doesn't exist, ``None`` is returned.
    :type exists: bool
    :returns: The url, width (x) and height (y).
    :rtype: :class:`ThumbDict` with keys url, x, y OR ``None``

    """
    if not item:
        return None

    image_dir, item_id = _normalize_thumb_item(item)
    url = thumb_url(item, size, qualified, exists)

    if not url:
        return None
    return ThumbDict(url, config['thumb_sizes'][image_dir][size])

def resize_thumb(img, size, filter=Image.ANTIALIAS):
    """Resize an image without any stretching by cropping when necessary.

    If the given image has a different aspect ratio than the requested
    size, the tops or sides will be cropped off before resizing.

    Note that stretching will still occur if the target size is larger
    than the given image.

    :param img: Any open image
    :type img: :class:`PIL.Image`
    :param size: The desired width and height
    :type size: tuple
    :param filter: The downsampling filter to use when resizing.
        Defaults to PIL.Image.ANTIALIAS, the highest possible quality.
    :returns: A new, resized image instance

    """
    X, Y, X2, Y2 = 0, 1, 2, 3 # aliases for readability

    src_ratio = float(img.size[X]) / img.size[Y]
    dst_ratio = float(size[X]) / size[Y]

    if dst_ratio != src_ratio and (img.size[X] >= size[X] and
                                   img.size[Y] >= size[Y]):
        crop_size = list(img.size)
        crop_rect = [0, 0, 0, 0] # X, Y, X2, Y2

        if dst_ratio < src_ratio:
            crop_size[X] = int(crop_size[Y] * dst_ratio)
            crop_rect[X] = int(float(img.size[X] - crop_size[X]) / 2)
        else:
            crop_size[Y] = int(crop_size[X] / dst_ratio)
            crop_rect[Y] = int(float(img.size[Y] - crop_size[Y]) / 2)

        crop_rect[X2] = crop_rect[X] + crop_size[X]
        crop_rect[Y2] = crop_rect[Y] + crop_size[Y]

        img = img.crop(crop_rect)

    return img.resize(size, filter)

def create_thumbs_for(item, image_file, image_filename):
    """Creates thumbnails in all sizes for a given Media or Podcast object.

    Side effects: Closes the open file handle passed in as image_file.

    :param item: A 2-tuple with a subdir name and an ID. If given a
        ORM mapped class with _thumb_dir and id attributes, the info
        can be extracted automatically.
    :type item: ``tuple`` or mapped class instance
    :param image_file: An open file handle for the original image file.
    :type image_file: file
    :param image_filename: The original filename of the thumbnail image.
    :type image_filename: unicode
    """
    image_dir, item_id = _normalize_thumb_item(item)
    img = Image.open(image_file)

    # TODO: Allow other formats?
    for key, xy in config['thumb_sizes'][item._thumb_dir].iteritems():
        path = thumb_path(item, key)
        thumb_img = resize_thumb(img, xy)
        if thumb_img.mode != "RGB":
            thumb_img = thumb_img.convert("RGB")
        thumb_img.save(path)

    # Backup the original image just for kicks
    backup_type = os.path.splitext(image_filename)[1].lower()[1:]
    backup_path = thumb_path(item, 'orig', ext=backup_type)
    backup_file = open(backup_path, 'w+b')
    image_file.seek(0)
    shutil.copyfileobj(image_file, backup_file)
    image_file.close()
    backup_file.close()

def create_default_thumbs_for(item):
    """Create copies of the default thumbs for the given item.

    This copies the default files (all named with an id of 'new') to
    use the given item's id. This means there could be lots of duplicate
    copies of the default thumbs, but at least we can always use the
    same url when rendering.

    :param item: A 2-tuple with a subdir name and an ID. If given a
        ORM mapped class with _thumb_dir and id attributes, the info
        can be extracted automatically.
    :type item: ``tuple`` or mapped class instance

    """
    image_dir, item_id = _normalize_thumb_item(item)
    for key in config['thumb_sizes'][image_dir].iterkeys():
        src_file = thumb_path((image_dir, 'new'), key)
        dst_file = thumb_path(item, key)
        shutil.copyfile(src_file, dst_file)

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
    xhtml = pylons.templating.render_genshi(
        'media/_embeddable_player.html',
        extra_vars=dict(media=media),
        method='xhtml'
    )
    xhtml = spaces_between_tags.sub(literal('><'), xhtml)
    return xhtml.strip()

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


class Player(object):
    """Abstract Player Class"""
    is_flash = False
    is_embed = False
    is_html5 = False

class FlowPlayer(Player):
    """Flash-based FlowPlayer"""
    is_flash = True

    @staticmethod
    def adjust_dimensions(media, file, width, height):
        return width, height + player_controls_heights.get('flowplayer', 0)

    @staticmethod
    def swf_url(media, file, qualified=False):
        return url_for('/scripts/third-party/flowplayer-3.1.5.swf', qualified=qualified)

    @staticmethod
    def flashvars(media, file, autoplay=False, autobuffer=False, qualified=False):
        playlist = []
        vars = {
            'canvas': {'backgroundColor': '#000', 'backgroundGradient': 'none'},
            'clip': {'scaling': 'fit'},
            'playlist': playlist,
        }

        # Show a preview image
        if media.type == AUDIO or not autoplay:
            playlist.append({
                'url': thumb_url(media, 'l', qualified=qualified),
                'autoPlay': True,
                'autoBuffer': True,
            })

        playlist.append({
            'url': file.play_url(qualified=qualified),
            'autoPlay': autoplay,
            'autoBuffer': autoplay or autobuffer,
        })

        # Flowplayer wants these options passed as an escaped JSON string
        # inside a single 'config' flashvar. When using the flowplayer's
        # own JS, this is automatically done, but since we use Swiff, a
        # SWFObject clone, we have to do this ourselves.
        vars = {'config': json.dumps(vars, separators=(',', ':'))}
        return vars

class JWPlayer(Player):
    """Flash-based JWPlayer -- this can play YouTube videos!"""
    is_flash = True

    @staticmethod
    def adjust_dimensions(media, file, width, height):
        return width, height + player_controls_heights.get('jwplayer', 0)

    @staticmethod
    def swf_url(media, file, qualified=False):
        return url_for('/scripts/third-party/jw_player/player.swf', qualified=qualified)

    @staticmethod
    def flashvars(media, file, autoplay=False, autobuffer=False, qualified=False):
        vars = {
            'image': thumb_url(media, 'l'),
            'autostart': autoplay,
        }
        providers = {
            AUDIO: 'sound',
            VIDEO: 'video',
        }

        if file.container == 'youtube':
            vars['provider'] = 'youtube'
            vars['file'] = file.link_url(qualified=qualified)
        else:
            vars['provider'] = providers[file.type]
            vars['file'] = file.play_url(qualified=qualified)
            vars['type'] = file.container

        plugins = []
        audio_desc = media.audio_desc
        captions = media.captions
        if audio_desc:
            plugins.append('audiodescription');
            vars['audiodescription.file'] = audio_desc.play_url(qualified=qualified)
        if captions:
            plugins.append('captions');
            vars['captions.file'] = captions.play_url(qualified=qualified)
        if plugins:
            vars['plugins'] = ','.join(plugins)

        return vars

class EmbedPlayer(Player):
    """Generic third-party embed player.

    YouTube, Vimeo and Google Video can all be embedded in the same way.
    """
    is_embed = True
    is_flash = True

    @staticmethod
    def adjust_dimensions(media, file, width, height):
        return width, height + player_controls_heights.get(file.container, 0)

    @staticmethod
    def swf_url(media, file, qualified=False):
        return file.play_url(qualified=qualified)

    @staticmethod
    def flashvars(*args, **kwargs):
        return {}

class HTML5Player(Player):
    """Stub that says HTML5 <audio> / <video> tags should be used."""
    is_html5 = True

players = {
    'flowplayer': FlowPlayer,
    'jwplayer': JWPlayer,
    'youtube': EmbedPlayer,
    'google': EmbedPlayer,
    'vimeo': EmbedPlayer,
    'html5': HTML5Player,
    'sublime': HTML5Player,
}
"""Maps player names to classes that describe their behaviour.

The names are from the html5_player and flash_player settings.

You can use set 'youtube' to JWPlayer to take advantage of YouTube's
chromeless player. The only catch is that it doesn't support HD.
"""

player_controls_heights = {
    'youtube': 25,
    'google': 27,
    'flowplayer': 24,
    'jwplayer': 24,
}
"""The height of the controls for each player.

We increase the height of the player by this number of pixels to
maintain a 16:9 aspect ratio.
"""

def pick_podcast_media_file(files):
    """Return the best choice of files to play.

    XXX: This method uses the
         :ref:`~mediacore.lib.filetypes.pick_media_file_player` method and
         comes with the same caveats.

    :param files: :class:`~mediacore.model.media.MediaFile` instances.
    :type files: list
    :returns: A :class:`~mediacore.model.media.MediaFile` object or None
    """
    return pick_media_file_player(files, browser='itunes', player_type='html5')[0]

def pick_any_media_file(files):
    """Return a file playable in at least one browser, with the current
    player_type setting, or None.

    XXX: This method uses the
         :ref:`~mediacore.lib.filetypes.pick_media_file_player` method and
         comes with the same caveats.

    :param files: :class:`~mediacore.model.media.MediaFile` instances.
    :type files: list
    :returns: A :class:`~mediacore.model.media.MediaFile` object or None
    """
    return pick_media_file_player(files, browser='chrome')[0]
