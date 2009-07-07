import re
import math
import datetime as dt
import time
from BeautifulSoup import BeautifulSoup
from urlparse import urlparse
from webhelpers import date, feedgenerator, html, number, misc, text, paginate
from webhelpers.html.converters import format_paragraphs
from webhelpers.html import tags
from routes.util import url_for
from tg import expose, request
from tg.exceptions import HTTPFound

from htmlsanitizer import Cleaner, Htmlator, valid_tags, valid_attrs, elem_map


class expose_xhr(object):
    def __call__(self, func):
        # create a wrapper function to override the template,
        # in the case that this is an xhr request
        def f(*args, **kwargs):
            if request.is_xhr:
               return self.xhr_decorator.__call__(func)(*args, **kwargs)
            else:
               return self.normal_decorator.__call__(func)(*args, **kwargs)

        # set up the normal decorator so that we have the correct
        # __dict__ properties to copy over. namely 'decoration'
        func = self.normal_decorator.__call__(func)

        # copy over all the special properties added to func
        for i in func.__dict__:
            f.__dict__[i] = func.__dict__[i]

        return f


    def __init__(self, template_norm='', template_xhr='json', **kwargs):
        self.normal_decorator = expose(template=template_norm, **kwargs)
        self.xhr_decorator = expose(template=template_xhr, **kwargs)


def duration_from_seconds(total_sec):
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


class MediaflowSlidePager(object):
    """Mediaflow Slide Paginator

    Slices rowsets into smaller groups for rendering over several slides.

    Usage:
        <div py:for="videos_slice in h.MediaflowSlidePager(page.items)" class="mediaflow-page">
            <ul>
                <li py:for="video in videos_slice">${video.title}</li>
            </ul>
        </div>
    """

    def __init__(self, items, items_per_slide=3, offset=0):
        self.items = items
        self.items_len = len(items)
        self.items_per_slide = items_per_slide
        self.offset = offset

    def __iter__(self):
        return self

    def next(self):
        if self.offset >= self.items_len:
            raise StopIteration
        next_offset = min(self.offset + self.items_per_slide, self.items_len)
        slice = self.items[self.offset:next_offset]
        self.offset = next_offset
        return slice


def slugify(string):
    string = str(string).lower()
    string = re.sub(r'\s+', u'-', string)
    string = re.sub(r'[^a-z0-9_-]', u'', string)
    string = re.sub(r'-+', u'-', string).strip('-')
    string = string.encode('ascii', 'ignore')
    return string[:50] # slugs are at most 50 chars in our database.


def redirect(*args, **kwargs):
    found = HTTPFound(location=url_for(*args, **kwargs)).exception
    raise found

tag_re = re.compile('<\s+>')
def clean_xhtml(string):
    """Markup cleaner

    Takes a string. If there is no markup in the string, applies
    paragraph formatting.

    Finally, runs the string through our XHTML cleaner.
    """
    if not tag_re.search(string):
        # there is no tag in the text, treat this post as plain text
        # and convert it to XHTML
        htmlator = Htmlator(encode_xml_specials=False, convert_newlines=True, make_links=True)
        string = htmlator(string)
    cleaner = Cleaner("strip_cdata", "encode_xml_specials")
    return cleaner(string)

def strip_xhtml(string):
    # remove carriage return chars; FIXME: is this necessary?
    string = string.replace("\r", "")
    return ''.join(BeautifulSoup(string).findAll(text=True))

def list_acceptable_xhtml():
    return dict(
        tags = ", ".join(sorted(valid_tags)),
        attrs = ", ".join(sorted(valid_attrs)),
        map = ", ".join(["%s -> %s" % (t, elem_map[t]) for t in elem_map])
    )

