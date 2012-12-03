# -*- coding: utf-8 -*-
# This file is a part of MediaCore CE, Copyright 2009-2012 MediaCore Inc.
# The source code in this file is dual licensed under the MIT license or the 
# GPL version 3 or (at your option) any later version.
# See LICENSE.txt in the main project directory, for more information.
#
# Copyright (c) 2012 Felix Schwarz <felix.schwarz@oss.schwarz.eu>

import os
import shutil
import tempfile

import pylons
from pylons.configuration import config

from mediacore.config.environment import load_environment
from mediacore.lib.test.pythonic_testcase import *
from mediacore.model.meta import DBSession, metadata
from mediacore.websetup import add_default_data


class DBTestCase(PythonicTestCase):
    
    enabled_plugins = ''
    
    def setUp(self):
        super(DBTestCase, self).setUp()
        self.env_dir = self._create_environment_folders()
        global_config = {
#            'debug': 'true', 
#            'error_email_from': 'paste@localhost', 
#            '__file__': '.../standalone.ini', 
#            'here': '...', 
#            'smtp_server': 'localhost'
        }
        app_config = {
            'plugins': self.enabled_plugins,
            'sqlalchemy.url': 'sqlite://', 
            'layout_template': 'layout', 
            'external_template': 'false',
            'image_dir': os.path.join(self.env_dir, 'images'), 
            'media_dir': os.path.join(self.env_dir, 'media'), 
            
#            'full_stack': 'true', 
#            'enable_gzip': 'true', 
#            'static_files': 'true', 
#            'sqlalchemy.echo': 'False', 
#            'file_serve_method': 'default', 
#            'app_instance_uuid': '', str(uuid.uuid4())
#            'media_dir': '.../data/media', 
#            'sqlalchemy.pool_recycle': '3600', 
#            'sa_auth.cookie_secret': 'superdupersecret', 
#            'cache_dir': '.../data', 
#            'beaker.session.key': 'mediacore', 
#            'beaker.session.secret': 'superdupersecret'
        }
        
        self.pylons_config = load_environment(global_config, app_config)
        metadata.create_all(bind=DBSession.bind, checkfirst=True)
        add_default_data()
        DBSession.commit()
        
        config.push_process_config(self.pylons_config)
    
    def _create_environment_folders(self):
        j = lambda *args: os.path.join(*args)
        
        env_dir = tempfile.mkdtemp()
        for name in ('appearance', 'images', j('images', 'media'), 'media', ):
            dirname = j(env_dir, name)
            os.mkdir(dirname)
        return env_dir
    
    def tearDown(self):
        self._tear_down_db()
        self._tear_down_pylons()
        shutil.rmtree(self.env_dir)
        super(DBTestCase, self).tearDown()
    
    def _tear_down_db(self):
        metadata.drop_all(bind=DBSession.bind)
        DBSession.close_all()
    
    def _tear_down_pylons(self):
        pylons.cache._pop_object()
        try:
            pylons.app_globals.settings_cache.clear()
            pylons.app_globals._pop_object()
        except TypeError:
            # The test might have not set up any app_globals
            # No object (name: app_globals) has been registered for this thread
            pass
        config.pop_process_config()
        DBSession.registry.clear()

