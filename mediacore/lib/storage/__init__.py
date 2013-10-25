# This file is a part of MediaDrop (http://www.mediadrop.net),
# Copyright 2009-2013 MediaDrop contributors
# For the exact contribution history, see the git revision log.
# The source code contained in this file is licensed under the GPLv3 or
# (at your option) any later version.
# See LICENSE.txt in the main project directory, for more information.

from mediacore.lib.storage.api import *

from mediacore.lib.storage.localfiles import LocalFileStorage
from mediacore.lib.storage.remoteurls import RemoteURLStorage
from mediacore.lib.storage.ftp import FTPStorage
from mediacore.lib.storage.youtube import YoutubeStorage
from mediacore.lib.storage.vimeo import VimeoStorage
from mediacore.lib.storage.bliptv import BlipTVStorage
from mediacore.lib.storage.googlevideo import GoogleVideoStorage
from mediacore.lib.storage.dailymotion import DailyMotionStorage

# provide a unified API, everything storage-related should be available from
# this module
from mediacore.lib.uri import StorageURI

