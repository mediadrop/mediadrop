# -*- coding: utf-8 -*-
# This file is a part of MediaDrop (http://www.mediadrop.net),
# Copyright 2009-2013 MediaDrop contributors
# For the exact contribution history, see the git revision log.
# The source code in this file is is dual licensed under the MIT license or
# the GPLv3 or (at your option) any later version.
# See LICENSE.txt in the main project directory, for more information.

import os
import shutil
import tempfile

import pylons
from pylons.configuration import config

from mediadrop.lib.test.pythonic_testcase import *
from mediadrop.lib.test.support import setup_environment_and_database
from mediadrop.model.meta import DBSession, metadata
from mediadrop.websetup import add_default_data


class DBTestCase(PythonicTestCase):
    
    enabled_plugins = ''
    
    def setUp(self):
        super(DBTestCase, self).setUp()
        self.env_dir = self._create_environment_folders()
        self.pylons_config = setup_environment_and_database(self.env_dir, 
            enabled_plugins=self.enabled_plugins)
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

