# This file is a part of MediaCore CE, Copyright 2009-2012 MediaCore Inc.
# The source code contained in this file is licensed under the GPL.
# See LICENSE.txt in the main project directory, for more information.

from mediacore.tests import *

class TestApiMediaController(TestController):

    def test_index(self):
        response = self.app.get(url(controller='api/media', action='index'))
        # Test response...
