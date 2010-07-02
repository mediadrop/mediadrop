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

import os
import re
import shutil
import urllib2
import simplejson
from PIL import Image
import gdata.youtube
import gdata.youtube.service
# XXX: note that pylons.url is imported here. Make sure to only use it with
#      absolute paths (ie. those starting with a /) to avoid differences in
#      behavior from mediacore.lib.helpers.url_for
from pylons import config, url as url_for
from mediacore import __version__ as VERSION
from mediacore.lib.compat import max

import logging
log = logging.getLogger(__name__)

__all__ = [
    'ThumbDict', 'create_default_thumbs_for', 'create_thumbs_for',
    'get_embed_details_youtube', 'get_embed_details_google', 'get_embed_details_vimeo',
    'thumb', 'thumb_path', 'thumb_paths', 'thumb_url',
]

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

def get_embed_details_youtube(id):
    """Given a YouTube video ID, return the associated thumbnail URL and
    the duration of the video.

    :param id: a valid YouTube video ID
    :type id: string
    :returns: Thumbnail URL (or None), and duration (or None)
    :rtype: tuple (string, int)
    """
    yt_service = gdata.youtube.service.YouTubeService()
    yt_service.ssl = False
    entry = yt_service.GetYouTubeVideoEntry(video_id=id)
    duration = int(entry.media.duration.seconds)
    tn = max(entry.media.thumbnail, key=lambda tn: int(tn.width))
    thumb_url = tn.url

    return thumb_url, duration

google_image_rgx = re.compile(r'media:thumbnail url="([^"]*)"')
google_duration_rgx = re.compile(r'duration="([^"]*)"')
def get_embed_details_google(id):
    """Given a Google Video ID, return the associated thumbnail URL and
    the duration of the video.

    :param id: a valid Google Video ID
    :type id: string
    :returns: Thumbnail URL (or None), and duration (or None)
    :rtype: tuple (string, int)
    """
    google_data_url = 'http://video.google.com/videofeed?docid=%s' % id
    thumb_url = None
    duration = None
    from mediacore.lib.helpers import decode_entities
    try:
        temp_data = urllib2.urlopen(google_data_url)
        data = temp_data.read()
        temp_data.close()
        thumb_match = google_image_rgx.search(data)
        dur_match = google_duration_rgx.search(data)
        if thumb_match:
            thumb_url = decode_entities(thumb_match.group(1))
        if dur_match:
            duration = int(dur_match.group(1))
    except urllib2.URLError, e:
        log.exception(e)

    return thumb_url, duration

def get_embed_details_vimeo(id):
    """Given a Vimeo video ID, return the associated thumbnail URL and
    the duration of the video.

    :param id: a valid Vimeo video ID
    :type id: string
    :returns: Thumbnail URL (or None), and duration (or None)
    :rtype: tuple (string, int)
    """
    # Vimeo API requires us to give a user-agent, to avoid 403 errors.
    headers = {
        'User-Agent': 'MediaCore %s' % VERSION,
    }
    vimeo_data_url = 'http://vimeo.com/api/v2/video/%s.%s' % (id, 'json')
    req = urllib2.Request(vimeo_data_url, headers=headers)
    thumb_url = None
    duration = None
    try:
        temp_data = urllib2.urlopen(req)
        data = simplejson.loads(temp_data.read())
        temp_data.close()
        thumb_url = data[0]['thumbnail_large']
        duration = int(data[0]['duration'])
    except urllib2.URLError, e:
        log.exception(e)

    return thumb_url, duration
