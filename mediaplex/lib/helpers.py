from webhelpers import date, feedgenerator, html, number, misc, text, paginate
from webhelpers.html.converters import format_paragraphs

def duration_from_seconds(total_sec):
    from math import floor
    secs = total_sec % 60
    mins = floor(total_sec / 60)
    hours = floor(total_sec / 360)
    if hours > 0:
        return '%d:%02d:%02d' % (hours, mins, secs)
    else:
        return '%d:%02d' % (mins, secs)

def video_player(url):
    import re
    urlparts = re.match(r'https?://(www\.)?([^/]+)/(.*)', str(url))
    domain = urlparts.group(2)

    if domain in ('youtube.com', 'video.google.com'):
        # Google Video's embed code uses 400 x 326
        xhtml = u'<object type="application/x-shockwave-flash" width="%(width)d" height="%(height)d" data="%(url)s" id="video-player"><param name="movie" value="%(url)s" /></object>'\
            % {'url': url, 'width': 479, 'height': 383}
    elif domain == 'godtube.com':
        # http://godtube.com/view_video.php?viewkey=4ce7f62c8fa7541273d6
        xhtml = u'<embed src="http://godtube.com/flvplayer.swf" FlashVars="%(viewkey)s" wmode="transparent" quality="high" width="479" height="383" name="godtube" align="middle" allowScriptAccess="sameDomain" type="application/x-shockwave-flash" pluginspage="http://www.macromedia.com/go/getflashplayer" /></embed>' \
            % {'viewkey': url.split('?')[1]}
    else:
        xhtml = 'FLOW PLAYER NOT YET IMPLEMENTED'
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
