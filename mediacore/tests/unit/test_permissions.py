# This file is a part of MediaCore CE, Copyright 2009-2012 MediaCore Inc.
# The source code contained in this file is licensed under the GPL.
# See LICENSE.txt in the main project directory, for more information.

from mediacore.tests import *
import pylons
import os, pwd, grp, stat
from mediacore.model import Media, Podcast

class TestPermissions(TestController):

    def __init__(self, *args, **kwargs):
        TestController.__init__(self, *args, **kwargs)

        # Initialize pylons.app_globals, etc. for use in main thread.
        self.response = self.app.get('/_test_vars')
        pylons.app_globals._push_object(self.response.app_globals)
        pylons.config._push_object(self.response.config)

        # Attempt to get uname/uid, gname/gids from the config file.
        self.user_name, self.user_id = self._configured_user()
        self.group_names, self.group_ids = self._configured_groups()

        # Fall back to the current user/groups.
        if not self.user_id:
            self.user_name, self.user_id = self._current_user()
        if not self.group_ids:
            self.group_names, self.group_ids = self._current_groups()

    def _configured_user(self):
        if 'server_user' in pylons.config:
            name = pylons.config['server_user']
            id = pwd.getpwnam(name)[2]
            return name, id
        else:
            return None, None

    def _configured_groups(self):
        if 'server_groups' in pylons.config:
            names = [x.strip() for x in pylons.config['server_group'].split(',')]
            ids = [grp.getgrnam(x)[0] for x in names]
            return names, ids
        else:
            return None, None

    def _current_user(self):
        name = pwd.getpwuid(os.getuid())[0]
        id = os.getuid()
        return name, id

    def _current_groups(self):
        ids = os.getgroups()
        names = [grp.getgrgid(x)[0] for x in ids]
        return names, ids

    def _test_writable(self, dir):
        # dir must be a directory
        assert os.path.isdir(dir) == True, "%s is not a directory" % dir

        stats = os.stat(dir)
        mode = stats[stat.ST_MODE]
        uid = stats[stat.ST_UID]
        gid = stats[stat.ST_GID]

        # Is the folder read/writable by the user?
        user_read = (mode & stat.S_IRUSR) != 0
        user_write = (mode & stat.S_IWUSR) != 0
        user_traverse = (mode & stat.S_IXUSR) != 0
        group_read = (mode & stat.S_IRGRP) != 0
        group_write = (mode & stat.S_IWGRP) != 0
        group_traverse = (mode & stat.S_IXGRP) != 0
        other_read = (mode & stat.S_IROTH) != 0
        other_write = (mode & stat.S_IWOTH) != 0
        other_traverse = (mode & stat.S_IXOTH) != 0

        user_writeable = \
            uid == self.user_id \
            and (user_read or other_read) \
            and (user_write or other_write) \
            and (user_traverse or other_traverse)

        group_writeable = \
            gid in self.group_ids \
            and (group_read or other_read) \
            and (group_write or other_write) \
            and (group_traverse or other_traverse)

        if not user_writeable and not group_writeable:
            raise Exception(
            "%s does not appear to be writeable by the specified server user "\
            "or group.\nCurrently specified server user: %s\n"\
            "Currently specified server groups: %s\n"\
            "You can specify different users and groups by using the "\
            "'server_user' and 'server_groups' settings in the config (.ini) file."\
            % (dir, self.user_name, ", ".join(self.group_names))
            )

    def test_cache_dir(self):
        self._test_writable(pylons.config['pylons.cache_dir'])

    def test_image_dir(self):
        self._test_writable(pylons.config['image_dir'])

    def test_media_dir(self):
        self._test_writable(pylons.config['media_dir'])

    def test_deleted_files_dir(self):
        self._test_writable(pylons.config['deleted_files_dir'])

    def test_deleted_media_dir(self):
        # It doesn't really matter if this dir doesn't exist, so long as the
        # deleted_files_dir is writeable, because MediaCore will create it
        path = pylons.config['deleted_files_dir'] + os.sep + Media._thumb_dir
        if os.path.exists(path):
            self._test_writable(path)

    def test_deleted_podcast_dir(self):
        # It doesn't really matter if this dir doesn't exist, so long as the
        # deleted_files_dir is writeable, because MediaCore will create it
        path = pylons.config['deleted_files_dir'] + os.sep + Podcast._thumb_dir
        if os.path.exists(path):
            self._test_writable(path)
