# This file is a part of MediaDrop (http://www.mediadrop.net),
# Copyright 2009-2013 MediaDrop contributors
# For the exact contribution history, see the git revision log.
# The source code contained in this file is licensed under the GPLv3 or
# (at your option) any later version.
# See LICENSE.txt in the main project directory, for more information.


from __future__ import absolute_import

import os
import sys

import paste
from paste.fixture import TestApp
from paste.deploy import appconfig, loadapp
from paste.script.util import logging_config


__all__ = ['init_mediadrop']


def init_mediadrop(config_filename, here_dir=None, disable_logging=False):
    if here_dir is None:
        here_dir = os.getcwd()
    if not disable_logging:
        logging_config.fileConfig(config_filename)

    config_name = 'config:%s' % config_filename
    # XXX: Note, initializing CONFIG here is Legacy support. pylons.config
    # will automatically be initialized and restored via the registry
    # restorer along with the other StackedObjectProxys
    # Load app config into paste.deploy to simulate request config
    # Setup the Paste CONFIG object, adding app_conf/global_conf for legacy
    # code
    conf = appconfig(config_name, relative_to=here_dir)
    conf.update(dict(app_conf=conf.local_conf,
                     global_conf=conf.global_conf))
    paste.deploy.config.CONFIG.push_thread_config(conf)

    # Load locals and populate with objects for use in shell
    sys.path.insert(0, here_dir)

    # Load the wsgi app first so that everything is initialized right
    wsgiapp = loadapp(config_name, relative_to=here_dir)
    test_app = TestApp(wsgiapp)

    # Query the test app to setup the environment
    tresponse = test_app.get('/_test_vars')
    request_id = int(tresponse.body)

    # Disable restoration during test_app requests
    test_app.pre_request_hook = lambda self: paste.registry.restorer.restoration_end()
    test_app.post_request_hook = lambda self: paste.registry.restorer.restoration_begin(request_id)

    # Restore the state of the Pylons special objects (StackedObjectProxies)
    paste.registry.restorer.restoration_begin(request_id)

