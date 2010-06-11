"""The application's Globals object"""

from beaker.cache import CacheManager
from beaker.util import parse_cache_config_options

class CachedSettingsDict(object):
    """
    A caching descriptor for the application settings from our database.

    Queries the database when first accessed, and after the cache expires::

        from pylons import app_globals
        some_value = app_globals.settings[some_key]

    """
    def __init__(self, namespace='app_settings', expire=3600):
        self.namespace = namespace
        self.expire = expire
        self.cache = None

    def __get__(self, instance, owner):
        """Fetch the settings and cache for 6 minutes.

        :param instance: Our :class:`Globals` instance for this app.
        :param owner: The :class:`Globals` class.
        :returns: All our settings
        :rtype: dict

        """
        if instance is None:
            raise AttributeError, 'Settings cannot be accessed staticly, '\
                'use pylons.app_globals.settings instead.'
        if self.cache is None:
            self.cache = instance.cache.get_cache(self.namespace,
                                                  expire=self.expire,
                                                  type='memory')
        return self.cache.get(key=None, createfunc=self.fetch_settings)

    def fetch_settings(self):
        from mediacore.model import DBSession, Setting
        return dict(DBSession.query(Setting.key, Setting.value))

class Globals(object):
    """Globals acts as a container for objects available throughout the
    life of the application

    """
    settings = CachedSettingsDict()

    def __init__(self, config):
        """One instance of Globals is created during application
        initialization and is available during requests via the
        'app_globals' variable

        """
        self.cache = CacheManager(**parse_cache_config_options(config))
