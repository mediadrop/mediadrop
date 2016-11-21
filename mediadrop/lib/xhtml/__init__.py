# This file is a part of MediaDrop (http://www.mediadrop.video),
# Copyright 2009-2015 MediaDrop contributors
# For the exact contribution history, see the git revision log.
# The source code contained in this file is licensed under the GPLv3 or
# (at your option) any later version.
# See LICENSE.txt in the main project directory, for more information.
"""
Our own XHTML sanitation helpers

"""
from copy import copy
import re

from bleach import clean, linkify, DEFAULT_CALLBACKS
from bleach.callbacks import target_blank
from webhelpers import text

from mediadrop.lib.xhtml.htmlsanitizer import (
    entities_to_unicode as decode_entities,
    encode_xhtml_entities as encode_entities)

__all__ = [
    'clean_xhtml',
    'decode_entities',
    'encode_entities',
    'excerpt_xhtml',
    'line_break_xhtml',
    'list_acceptable_xhtml',
    'strip_xhtml',
    'truncate_xhtml',
]

# Configuration for HTML sanitization
blank_line = re.compile("\s*\n\s*\n\s*", re.M)
block_tags = 'p br pre blockquote div h1 h2 h3 h4 h5 h6 hr ul ol li form table tr td tbody thead'.split()
block_spaces = re.compile("\s*(</{0,1}(" + "|".join(block_tags) + ")>)\s*", re.M)
block_close = re.compile("(</(" + "|".join(block_tags) + ")>)", re.M)
valid_tags = 'p i em strong b u a br pre abbr ol ul li sub sup ins del blockquote cite'.split() + block_tags
valid_attrs = {
    '*': ['class', 'style'],
    'img': ['src alt'],
    'a': 'href rel title target'.split(),
    }
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
    tags = valid_tags,
    attributes = valid_attrs,
)


def clean_xhtml(string, p_wrap=True, _cleaner_settings=None):
    """Convert the given plain text or HTML into valid XHTML.

    If there is no markup in the string, apply paragraph formatting.

    :param string: XHTML input string
    :type string: unicode
    :param p_wrap: Wrap the output in <p></p> tags?
    :type p_wrap: bool
    :param _cleaner_settings: Constructor kwargs for
        :class:`mediadrop.lib.htmlsanitizer.Cleaner`
    :type _cleaner_settings: dict
    :returns: XHTML
    :rtype: unicode
    """
    if not string or not string.strip():
        # If the string is none, or empty, or whitespace
        return u""

    if _cleaner_settings is None:
        _cleaner_settings = cleaner_settings
    callbacks = copy(DEFAULT_CALLBACKS)
    add_target_blank = _cleaner_settings.pop('add_target_blank', False)
    if add_target_blank:
        callbacks.append(target_blank)

    # remove carriage return chars; FIXME: is this necessary?
    string = string.replace(u"\r", u"")

    # remove non-breaking-space characters. FIXME: is this necessary?
    string = string.replace(u"\xa0", u" ")
    string = string.replace(u"&nbsp;", u" ")

    # replace all blank lines with <br> tags
    string = blank_line.sub(u"<br/>", string)

    # initialize and run the cleaner
    string = clean(string, **_cleaner_settings)
    # Convert links and add nofolllow and target
    string = linkify(string, callbacks=callbacks)

    # Wrap in a <p> tag when no tags are used, and there are no blank
    # lines to trigger automatic <p> creation
    # FIXME: This should trigger any time we don't have a wrapping block tag
    # FIXME: This doesn't wrap orphaned text when it follows a <p> tag, for ex
    if p_wrap \
        and (not string.startswith('<p>') or not string.endswith('</p>')):
        string = u"<p>%s</p>" % string

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
            string = clean(string, **cleaner_settings)

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
    # Strip all xhtml:
    string = clean(string, strip=True, tags=[], attributes=[])

    # Decode entities and strip hidden xhtml markup:
    string = decode_entities(string)

    # Note that decode_entities() call above takes care of xhtml
    #   striping of hidden markup, and clean() below will re-encode
    #   escapable characters if they got removed and we weren't
    #   supposed to unescape them:
    if not _decode_entities:
        string = clean(string)

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
