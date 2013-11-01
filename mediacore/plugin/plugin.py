# This file is a part of MediaDrop (http://www.mediadrop.net),
# Copyright 2009-2013 MediaDrop contributors
# For the exact contribution history, see the git revision log.
# The source code contained in this file is licensed under the GPLv3 or
# (at your option) any later version.
# See LICENSE.txt in the main project directory, for more information.

import logging
import os

from importlib import import_module
import pkg_resources
from pkg_resources import resource_exists, resource_filename
from pylons.util import class_name_from_module_name
from routes.util import controller_scan


__all__ = ['MediaDropPlugin']

log = logging.getLogger(__name__)


class MediaDropPlugin(object):
    """
    Plugin Metadata

    This houses all the conventions for where resources should be found
    within a plugin module. A plugin author could potentially extend this
    class to redefine these conventions according to their needs. Besides
    that, it gives us a convenient place to store this data for repeated
    use.

    """
    def __init__(self, module, name, templates_path=None,
                 public_path=None, controllers=None, locale_dirs=None):
        self.module = module
        self.modname = module.__name__
        self.name = name
        self.package_name = self._package_name()
        self.templates_path = templates_path or self._default_templates_path()
        self.public_path = public_path or self._default_public_path()
        self.controllers = controllers or self._default_controllers()
        self.locale_dirs = self._default_locale_dirs()
        # migrations.util imports model and that causes all kind of recursive
        # import trouble with mediacore.plugin (events)
        from mediacore.migrations import PluginDBMigrator
        self.migrator_class = PluginDBMigrator

    def _package_name(self):
        pkg_provider = pkg_resources.get_provider(self.modname)
        module_path = self.modname.replace('.', os.sep)
        is_package = pkg_provider.module_path.endswith(module_path)
        if is_package:
            return self.modname
        return self.modname.rsplit('.', 1)[0]

    def _default_templates_path(self):
        if resource_exists(self.modname, 'templates'):
            return resource_filename(self.modname, 'templates')
        return None

    def _default_locale_dirs(self):
        if resource_exists(self.modname, 'i18n'):
            localedir = resource_filename(self.modname, 'i18n')
            return {self.name: localedir}
        return None

    def _default_public_path(self):
        if resource_exists(self.modname, 'public'):
            return resource_filename(self.modname, 'public')
        return None

    def _default_controllers(self):
        # Find controllers in the root plugin __init__.py
        controller_class = _controller_class_from_module(self.module, self.name)
        if controller_class:
            class_name = controller_class.__module__ + '.' + controller_class.__name__
            log.debug('Controller loaded; "%s" = %s' % (self.name, class_name))
            return {self.name: controller_class}

        # Search a controllers directory, standard pylons style
        if not resource_exists(self.package_name, 'controllers'):
            log.debug('no controllers found for %r plugin.' % self.name)
            return {}
        controllers = {}
        directory = resource_filename(self.package_name, 'controllers')
        for name in controller_scan(directory):
            module_name = '.'.join([self.package_name, 'controllers',
                                    name.replace('/', '.')])
            module = import_module(module_name)
            mycontroller = _controller_class_from_module(module, name)
            if mycontroller is None:
                log.warn('Controller %r expected but not found in: %r', name, module)
                continue
            controllers[self.name + '/' + name] = mycontroller
            class_name = mycontroller.__module__ + '.' + mycontroller.__name__
            log.debug('Controller loaded; "%s" = %s' % (self.name + '/' + name, class_name))
        return controllers

    def contains_migrations(self):
        return (resource_exists(self.package_name, 'migrations') and 
            not resource_exists(self.package_name+'.migrations', 'alembic.ini'))

def _controller_class_from_module(module, name):
    c = getattr(module, '__controller__', None)
    if c is None:
        name = name.rsplit('/', 1)[-1]
        class_name = class_name_from_module_name(name) + 'Controller'
        c = getattr(module, class_name, None)
    return c
