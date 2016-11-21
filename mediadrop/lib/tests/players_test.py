# -*- coding: utf-8 -*-
# This file is a part of MediaDrop (http://www.mediadrop.video),
# Copyright 2009-2015 MediaDrop contributors
# For the exact contribution history, see the git revision log.
# The source code in this file is dual licensed under the MIT license or
# the GPLv3 or (at your option) any later version.
# See LICENSE.txt in the main project directory, for more information.

from mediadrop.lib.filetypes import VIDEO
from mediadrop.lib.players import FileSupportMixin, RTMP
from mediadrop.lib.test.pythonic_testcase import *
from mediadrop.lib.uri import StorageURI
from mediadrop.model import MediaFile


class FileSupportMixinTest(PythonicTestCase):
    def test_can_play_ignores_empty_container(self):
        class FakePlayer(FileSupportMixin):
            supported_containers = set(['mp4'])
            supported_schemes = set([RTMP])
        fake_player = FakePlayer()
        media_file = MediaFile()
        media_file.container = ''
        media_file.type = VIDEO
        uri = StorageURI(media_file, 'rtmp', 'test',
            server_uri='rtmp://stream.host.example/play')
        assert_equals('', uri.file.container,
            message='It is important that the server uri has no container.')
        assert_equals((True, ), fake_player.can_play([uri]))

import unittest
def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(FileSupportMixinTest))
    return suite
