# -*- coding: utf-8 -*-
# This file is a part of MediaDrop (http://www.mediadrop.net),
# Copyright 2009-2013 MediaDrop contributors
# For the exact contribution history, see the git revision log.
# The source code contained in this file is licensed under the GPLv3 or
# (at your option) any later version.
# See LICENSE.txt in the main project directory, for more information.

from mediacore.lib.storage.youtube import YoutubeStorage
from mediacore.lib.test.pythonic_testcase import *


class YoutubeStorageTest(PythonicTestCase):
    
    def youtube_id(self, url):
        match = YoutubeStorage.url_pattern.match(url)
        if match is None:
            return None
        return match.group('id')
    
    def assert_can_parse(self, url):
        assert_equals('RIk8A4TrCIY', self.youtube_id(url))
    
    def test_can_parse_youtube_com_watch_link(self):
        self.assert_can_parse('http://youtube.com/watch?v=RIk8A4TrCIY')
        self.assert_can_parse('http://www.youtube.com/watch?v=RIk8A4TrCIY')
        self.assert_can_parse('http://www.youtube.com/watch?feature=player_embedded&v=RIk8A4TrCIY')
    
    def test_accepts_https(self):
        self.assert_can_parse('https://youtube.com/watch?v=RIk8A4TrCIY')
        self.assert_can_parse('https://www.youtube.com/watch?v=RIk8A4TrCIY')
    
    def test_accepts_embeded_player(self):
        self.assert_can_parse('http://youtube.com/embed/RIk8A4TrCIY')
        self.assert_can_parse('https://www.youtube.com/embed/RIk8A4TrCIY')


import unittest

def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(YoutubeStorageTest))
    return suite
    
if __name__ == '__main__':
    unittest.main(defaultTest='suite')
