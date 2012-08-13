# This file is a part of MediaCore CE, Copyright 2009-2012 MediaCore Inc.
# The source code contained in this file is licensed under the GPL.
# See LICENSE.txt in the main project directory, for more information.

from mediacore.lib.storage.api import (add_new_media_file, sort_engines,
    StorageError, StorageEngine)

from mediacore.lib.storage.localfiles import LocalFileStorage
from mediacore.lib.storage.remoteurls import RemoteURLStorage
from mediacore.lib.storage.ftp import FTPStorage
from mediacore.lib.storage.youtube import YoutubeStorage
from mediacore.lib.storage.vimeo import VimeoStorage
from mediacore.lib.storage.bliptv import BlipTVStorage
from mediacore.lib.storage.googlevideo import GoogleVideoStorage
from mediacore.lib.storage.dailymotion import DailyMotionStorage

