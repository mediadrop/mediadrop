# This file is a part of MediaDrop (http://www.mediadrop.net),
# Copyright 2009-2013 MediaDrop contributors
# For the exact contribution history, see the git revision log.
# The source code contained in this file is licensed under the GPLv3 or
# (at your option) any later version.
# See LICENSE.txt in the main project directory, for more information.
"""The application's Globals object"""

from beaker.cache import CacheManager
from beaker.util import parse_cache_config_options

class Globals(object):
    """Globals acts as a container for objects available throughout the
    life of the application

    """
    def __init__(self, config):
        """One instance of Globals is created during application
        initialization and is available during requests via the
        'app_globals' variable

        """
        self.cache = cache = CacheManager(**parse_cache_config_options(config))
        self.settings_cache = cache.get_cache('app_settings',
                                              expire=3600,
                                              type='memory')

        # We'll store the primary translator here for sharing between requests
        self.primary_language = None
        self.primary_translator = None

    @property
    def settings(self):
        def fetch_settings():
            from mediadrop.model import DBSession, Setting
            settings_dict = dict(DBSession.query(Setting.key, Setting.value))
            return settings_dict
        return self.settings_cache.get(createfunc=fetch_settings, key=None)
