from webhelpers import date, feedgenerator, html, number, misc, text
from webhelpers.html.converters import format_paragraphs

def duration_from_seconds(total_sec):
    from math import floor
    secs = total_sec % 60
    mins = floor(total_sec / 60)
    hours = floor(total_sec / 360)
    if hours > 0:
        return '%d:%d:%d' % (hours, mins, secs)
    else:
        return '%d:%d' % (mins, secs)

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
