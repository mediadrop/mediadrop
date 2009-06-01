import re
import math
import datetime as dt
from urlparse import urlparse
from webhelpers import date, feedgenerator, html, number, misc, text, paginate
from webhelpers.html.converters import format_paragraphs
from webhelpers.html import tags
from routes.util import url_for
from tg import expose, request

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


def video_player(video):
    urlparts = urlparse(video.url)
    if not urlparts[1]:
        xhtml = u'''<div><script src="/scripts/third-party/flowplayer-3.1.0.min.js" type="text/javascript"></script>
<a href="%(flash_url)s" style="display:block;width:479px;height:383px" id="flowplayer"></a>
<script type="text/javascript">
flowplayer("flowplayer", "/scripts/third-party/flowplayer-3.1.0.swf");
</script></div>
''' % {'flash_url': url_for(controller='/video', action='serve', slug=video.slug)}
    else:
        urlparts = re.match(r'https?://(www\.)?([^/]+)/(.*)', str(video.url))
        domain = urlparts.group(2)

        if domain in ('youtube.com', 'video.google.com'):
            # Google Video's embed code uses 400 x 326
            xhtml = u'<object type="application/x-shockwave-flash" width="%(width)d" height="%(height)d" data="%(url)s" id="video-player"><param name="movie" value="%(url)s" /></object>'\
                % {'url': video.url, 'width': 479, 'height': 383}
        elif domain == 'godtube.com':
            # http://godtube.com/view_video.php?viewkey=4ce7f62c8fa7541273d6
            xhtml = u'<embed src="http://godtube.com/flvplayer.swf" FlashVars="%(viewkey)s" wmode="transparent" quality="high" width="479" height="383" name="godtube" align="middle" allowScriptAccess="sameDomain" type="application/x-shockwave-flash" pluginspage="http://www.macromedia.com/go/getflashplayer" /></embed>' \
                % {'viewkey': video.url.split('?')[1]}

    return xhtml


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
    return string.encode('ascii')
