# This file is a part of MediaDrop (http://www.mediadrop.video),
# Copyright 2009-2015 MediaDrop contributors
# For the exact contribution history, see the git revision log.
# The source code contained in this file is licensed under the GPLv3 or
# (at your option) any later version.
# See LICENSE.txt in the main project directory, for more information.


from __future__ import absolute_import

import os

from paste.deploy import appconfig
from paste.registry import Registry
from paste.script.util import logging_config

from mediadrop.lib.i18n import setup_global_translator
from mediadrop.lib.test import fake_request, register_instance
from mediadrop.config.environment import load_environment


__all__ = ['init_mediadrop']

def init_mediadrop(config_filename, here_dir=None, disable_logging=False):
    if not os.path.exists(config_filename):
        raise IOError('Config file %r does not exist.' % config_filename)
    if here_dir is None:
        here_dir = os.getcwd()
    if not disable_logging:
        logging_config.fileConfig(config_filename)

    conf = appconfig('config:%s' % config_filename, relative_to=here_dir)
    pylons_config = load_environment(conf.global_conf, conf.local_conf)
    paste_registry = Registry()
    paste_registry.prepare()
    pylons_config['paste.registry'] = paste_registry
    
    app_globals = pylons_config['pylons.app_globals']
    register_instance(paste_registry, 'app_globals', app_globals)
    register_instance(paste_registry, 'config', pylons_config)
    fake_request(pylons_config, registry=paste_registry)
    setup_global_translator(registry=paste_registry)


