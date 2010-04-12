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

import re
import math
import datetime as dt
import time
import os
import genshi.core
import pylons.templating
import shutil
from copy import copy
from urlparse import urlparse
from datetime import datetime
from PIL import Image

from BeautifulSoup import BeautifulSoup
from webhelpers import date, feedgenerator, html, number, misc, text, paginate, containers
from webhelpers.html import tags
from webhelpers.html.converters import format_paragraphs
from paste.util import mimeparse
from tg import config, request
import tg.exceptions

from mediacore.lib.htmlsanitizer import Cleaner, entities_to_unicode as decode_entities, encode_xhtml_entities as encode_entities
from mediacore.lib.base import url_for, redirect, expose_xhr


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


def list_acceptable_xhtml():
    return dict(
        tags = ", ".join(sorted(valid_tags)),
        attrs = ", ".join(sorted(valid_attrs)),
        map = ", ".join(["%s -> %s" % (t, elem_map[t]) for t in elem_map])
    )

def accepted_extensions():
    """Return the extensions allowed for upload.

    :rtype: list
    """
    e = config.mimetype_lookup.keys()
    e = [x.lstrip('.') for x in e]
    e = sorted(e)
    return e

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
    :type item: ``tuple`` or mapped class
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
    image_path = os.path.join(config.image_dir, image)

    if exists and not os.path.isfile(image_path):
        return None
    return image_path

def thumb_url(item, size, qualified=False, exists=False):
    """Get the thumbnail url for the given item and size.

    :param item: A 2-tuple with a subdir name and an ID. If given a
        ORM mapped class with _thumb_dir and id attributes, the info
        can be extracted automatically.
    :type item: ``tuple`` or mapped class
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

    if exists and not os.path.isfile(os.path.join(config.image_dir, image)):
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
    :type item: ``tuple`` or mapped class
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
    return ThumbDict(url, config.thumb_sizes[image_dir][size])

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

def create_default_thumbs_for(item):
    """Create copies of the default thumbs for the given item.

    This copies the default files (all named with an id of 'new') to
    use the given item's id. This means there could be lots of duplicate
    copies of the default thumbs, but at least we can always use the
    same url when rendering.

    :param item: A 2-tuple with a subdir name and an ID. If given a
        ORM mapped class with _thumb_dir and id attributes, the info
        can be extracted automatically.
    :type item: ``tuple`` or mapped class

    """
    image_dir, item_id = _normalize_thumb_item(item)
    for key in config.thumb_sizes[image_dir].iterkeys():
        src_file = thumb_path((image_dir, 'new'), key)
        dst_file = thumb_path(item, key)
        shutil.copyfile(src_file, dst_file)

def best_json_content_type(accept=None, raise_exc=True):
    """Return the best possible JSON header we can return for a client.

    Sometimes we want to return JSON as ``text/plain``. On windows,
    Flash uploads always request ``text/\*`` so the proper
    ``application/json`` header won't work.

    :param accept: An HTTP Accept header, defaults to that of the
        current request.
    :type accept: string
    :param raise_exc: By default an webob.exc.HTTPNotAcceptable header
        will be raised if the given Accept header does not match any of
        the possible JSON content types.
    :type raise_exc: bool
    :raises webob.exc.HTTPNotAcceptable: If `raise_exc` is True
        and the given Accept header doesn't work for our json types.
    :returns: mimetype
    :rtype: string

    """
    desired_matches = mimeparse.desired_matches(
        ['application/json', 'text/plain'],
        accept or request.environ.get('HTTP_ACCEPT', '*/*'))
    if raise_exc and not desired_matches:
        raise tg.exceptions.HTTPNotAcceptable # 406
    return desired_matches[0]

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

def embeddable_player(media):
    """Return a string of XHTML for embedding our player on other sites.

    All URLs include the domain (they're fully qualified).

    Since this returns a plain string, it is automatically escaped by Genshi
    when called in a template.

    :param media: The item to embed
    :type media: :class:`mediacore.model.media.Media` instance
    :returns: XHTML
    :rtype: unicode

    """
    template_finder = config['pylons.app_globals'].dotted_filename_finder
    template_name = template_finder.get_dotted_filename(
        'mediacore.templates.media._embeddable_player',
        template_extension='.html'
    )
    xhtml = pylons.templating.render_genshi(
        template_name,
        extra_vars=dict(media=media),
        method='xhtml'
    )
    xhtml = excess_whitespace.sub(' ', xhtml)
    return xhtml.strip()

def get_featured_category():
    from mediacore.model import Category
    from mediacore.model.settings import fetch_setting
    feat_id = int(fetch_setting('featured_category'))
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
    return 'Admins' in request.environ\
        .get('repoze.who.identity', {})\
        .get('groups', '')
