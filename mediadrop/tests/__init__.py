# This file is a part of MediaDrop (http://www.mediadrop.net),
# Copyright 2009-2013 MediaDrop contributors
# For the exact contribution history, see the git revision log.
# The source code contained in this file is licensed under the GPLv3 or
# (at your option) any later version.
# See LICENSE.txt in the main project directory, for more information.

"""Pylons application test package

This package assumes the Pylons environment is already loaded, such as
when this script is imported from the `nosetests --with-pylons=test.ini`
command.

This module initializes the application via ``websetup`` (`paster
setup-app`) and provides the base testing objects.
"""
from unittest import TestCase

from paste.deploy import loadapp
from paste.script.appinstall import SetupCommand
from pylons import url
from routes.util import URLGenerator
from webtest import TestApp

import pylons.test

__all__ = [
    'environ',
    'TestCase',
    'TestController',
    'url',
]

# Invoke websetup with the current config file
#SetupCommand('setup-app').run([pylons.test.pylonsapp.config['__file__']])

environ = {}

class TestController(TestCase):
    __test__ = False

    def __init__(self, *args, **kwargs):
        wsgiapp = pylons.test.pylonsapp
        config = wsgiapp.config
        self.app = TestApp(wsgiapp)
        url._push_object(URLGenerator(config['routes.map'], environ))
        TestCase.__init__(self, *args, **kwargs)

    def _new_publishable_media(self, slug, name):
        from datetime import datetime
        from mediadrop.model import Author, Media
        media = Media()
        media.slug = slug
        media.title = name
        media.subtitle = None
        media.description = u"""<p>Description</p>"""
        media.description_plain = u"""Description"""
        media.author = Author(u'fake name', u'fake@email.com')
        media.publish_on = datetime.now()
        media.publishable = True
        media.reviewed = True
        media.encoded = False
        media.type = None
        return media
