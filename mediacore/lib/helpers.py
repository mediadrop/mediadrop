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
from urlparse import urlparse

from BeautifulSoup import BeautifulSoup
from webhelpers import date, feedgenerator, html, number, misc, text, paginate, containers
from webhelpers.html import tags
from webhelpers.html.converters import format_paragraphs
from routes.util import url_for as _routes_url
from tg import config, request
from mediacore.lib.htmlsanitizer import Cleaner, entities_to_unicode as decode_entities, encode_xhtml_entities as encode_entities
from mediacore.model.settings import fetch_setting
from mediacore.lib.base import url_for


def duration_from_seconds(total_sec):
    """Return the HH:MM:SS for a given number of seconds."""
    if not total_sec:
        return u''
    secs = total_sec % 60
    mins = math.floor(total_sec / 60)
    hours = math.floor(total_sec / 60 / 60)
    if hours > 0:
        return u'%d:%02d:%02d' % (hours, mins, secs)
    else:
        return u'%d:%02d' % (mins, secs)

def duration_to_seconds(duration):
    """Return the number of seconds in a given HH:MM:SS."""
    if not duration:
        return 0
    parts = str(duration).split(':')
    parts.reverse()
    i = 0
    total_secs = 0
    for part in parts:
        total_secs += int(part) * (60 ** i)
        i += 1
    return total_secs


blank_line = re.compile("\s*\n\s*\n\s*", re.M)
block_tags = 'p br pre blockquote div h1 h2 h3 h4 h5 h6 hr ul ol li form table tr td tbody thead'.split()
block_spaces = re.compile("\s*(</{0,1}(" + "|".join(block_tags) + ")>)\s*", re.M)
block_close = re.compile("(</(" + "|".join(block_tags) + ")>)", re.M)
valid_tags = dict.fromkeys('p i em strong b u a br pre abbr ol ul li sub sup ins del blockquote cite'.split())
valid_attrs = dict.fromkeys('href title'.split())
elem_map = {'b': 'strong', 'i': 'em'}
# Map all invalid block elements to be paragraphs.
for t in block_tags:
    if t not in valid_tags:
        elem_map[t] = 'p'
clean_filters = [
    "strip_comments", "rename_tags", "strip_tags",
    "strip_attrs", "strip_schemes", "strip_cdata",
    "br_to_p", "make_links", "add_nofollow",
    "encode_xml_specials", "clean_whitespace", "strip_empty_tags",
]
truncate_filters = [
    "strip_empty_tags"
]
cleaner_settings = dict(
    convert_entities = BeautifulSoup.ALL_ENTITIES,
    valid_tags = valid_tags,
    valid_attrs = valid_attrs,
    elem_map = elem_map,
)

def clean_xhtml(string):
    """Convert the given plain text or HTML into valid XHTML.

    If there is no markup in the string, apply paragraph formatting.

    :returns: XHTML
    :rtype: unicode
    """
    if not string or not string.strip():
        # If the string is none, or empty, or whitespace
        return u""

    # wrap string in paragraph tag, just in case
    string = u"<p>%s</p>" % string.strip()

    # remove carriage return chars; FIXME: is this necessary?
    string = string.replace(u"\r", u"")

    # remove non-breaking-space characters. FIXME: is this necessary?
    string = string.replace(u"\xa0", u" ")
    string = string.replace(u"&nbsp;", u" ")

    # replace all blank lines with <br> tags
    string = blank_line.sub(u"<br/>", string)

    # initialize and run the cleaner
    string = Cleaner(string, *clean_filters, **cleaner_settings)()
    # FIXME: It's possible that the rename_tags operation creates
    # some invalid nesting. e.g.
    # >>> c = Cleaner("", "rename_tags", elem_map={'h2': 'p'})
    # >>> c('<p><h2>head</h2></p>')
    # u'<p><p>head</p></p>'
    # This is undesirable, so here we... just re-parse the markup.
    # But this ... could be pretty slow.
    string = Cleaner(string, *clean_filters, **cleaner_settings)()

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
