# This file is a part of MediaDrop (http://www.mediadrop.net),
# Copyright 2009-2013 MediaDrop contributors
# For the exact contribution history, see the git revision log.
# The source code contained in this file is licensed under the GPLv3 or
# (at your option) any later version.
# See LICENSE.txt in the main project directory, for more information.

import filecmp
import os
import re
import shutil

from PIL import Image
# XXX: note that pylons.url is imported here. Make sure to only use it with
#      absolute paths (ie. those starting with a /) to avoid differences in
#      behavior from mediacore.lib.helpers.url_for
from pylons import config, url as url_for

import mediacore
from mediacore.lib.util import delete_files

__all__ = [
    'create_default_thumbs_for', 'create_thumbs_for', 'delete_thumbs',
    'has_thumbs', 'has_default_thumbs',
    'ThumbDict', 'thumb', 'thumb_path', 'thumb_paths', 'thumb_url',
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
    paths = dict((key, thumb_path(item, key, **kwargs))
                 for key in config['thumb_sizes'][image_dir].iterkeys())
    # We can only find the original image but examining the file system,
    # so only return it if exists is True.
    if kwargs.get('exists', False):
        for extname in ('jpg', 'png'):
            path = thumb_path(item, 'orig', **kwargs)
            if path:
                paths['orig'] = path
                break
    return paths

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
    image_path = os.path.join(config['image_dir'], image)

    if exists and not os.path.isfile(image_path):
        return None
    return url_for('/images/%s' % image, qualified=qualified)

class ThumbDict(dict):
    """Dict wrapper with convenient attribute access"""

    def __init__(self, url, dimensions):
        dict.__init__(self)
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

_ext_filter = re.compile(r'^\.([a-z0-9]*)')

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
        thumb_img.save(path, quality=90)

    # Backup the original image, ensuring there's no odd chars in the ext.
    # Thumbs from DailyMotion include an extra query string that needs to be
    # stripped off here.
    ext = os.path.splitext(image_filename)[1].lower()
    ext_match = _ext_filter.match(ext)
    if ext_match:
        backup_type = ext_match.group(1)
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
    mediacore_dir = os.path.join(os.path.dirname(mediacore.__file__), '..')
    image_dir, item_id = _normalize_thumb_item(item)
    for key in config['thumb_sizes'][image_dir].iterkeys():
        src_file = thumb_path((image_dir, 'new'), key)
        if not os.path.exists(src_file):
            default_image_dir = os.path.join(mediacore_dir, 'data', 'images', image_dir)
            src_file = thumb_path((default_image_dir, 'new'), key)
        dst_file = thumb_path(item, key)
        shutil.copyfile(src_file, dst_file)

def delete_thumbs(item):
    """Delete the thumbnails associated with the given item.

    :param item: A 2-tuple with a subdir name and an ID. If given a
        ORM mapped class with _thumb_dir and id attributes, the info
        can be extracted automatically.
    :type item: ``tuple`` or mapped class instance
    """
    image_dir, item_id = _normalize_thumb_item(item)
    thumbs = thumb_paths(item, exists=True).itervalues()
    delete_files(thumbs, image_dir)

def has_thumbs(item):
    """Return True if a thumb exists for this item.

    :param item: A 2-tuple with a subdir name and an ID. If given a
        ORM mapped class with _thumb_dir and id attributes, the info
        can be extracted automatically.
    :type item: ``tuple`` or mapped class instance
    """
    return bool(thumb_path(item, 's', exists=True))

def has_default_thumbs(item):
    """Return True if the thumbs for the given item are the defaults.

    :param item: A 2-tuple with a subdir name and an ID. If given a
        ORM mapped class with _thumb_dir and id attributes, the info
        can be extracted automatically.
    :type item: ``tuple`` or mapped class instance
    """
    image_dir, item_id = _normalize_thumb_item(item)
    return filecmp.cmp(thumb_path((image_dir, item_id), 's'),
                       thumb_path((image_dir, 'new'), 's'))
