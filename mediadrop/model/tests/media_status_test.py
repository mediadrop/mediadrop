# This file is a part of MediaDrop (http://www.mediadrop.net),
# Copyright 2009-2013 MediaDrop contributors
# For the exact contribution history, see the git revision log.
# The source code contained in this file is licensed under the GPLv3 or
# (at your option) any later version.
# See LICENSE.txt in the main project directory, for more information.

from ddt import ddt as DataDrivenTestCase, data

from mediadrop.model import DBSession, Media
from mediadrop.lib.filetypes import (guess_media_type_map, AUDIO, AUDIO_DESC, 
    CAPTIONS, VIDEO)
from mediadrop.lib.players import AbstractFlashPlayer, FlowPlayer
from mediadrop.lib.storage.api import add_new_media_file
from mediadrop.lib.test.db_testcase import DBTestCase
from mediadrop.lib.test.pythonic_testcase import *
from mediadrop.plugin import events
from mediadrop.plugin.events import observes

#import logging
#logging.basicConfig(level=logging.DEBUG)
media_suffixes = guess_media_type_map.keys()
video_types = filter(lambda key: guess_media_type_map[key] == VIDEO, media_suffixes)
audio_types = filter(lambda key: guess_media_type_map[key] == AUDIO, media_suffixes)
caption_types = filter(lambda key: guess_media_type_map[key] == CAPTIONS, media_suffixes)

@DataDrivenTestCase
class MediaStatusUpdatesTypeTest(DBTestCase):
    def setUp(self):
        super(MediaStatusUpdatesTypeTest, self).setUp()
        # prevent warning about missing handlers for logger 
        # "mediadrop.model.players" ("fetch_enabled_players()")
        self.init_flowplayer()
        self.media = Media.example()
    
    def init_flowplayer(self):
        AbstractFlashPlayer.register(FlowPlayer)
        FlowPlayer.inject_in_db(enable_player=True)
    
    def add_external_file(self, media, file_suffix='mp4'):
        url = u'http://site.example/videos.%s' % file_suffix
        previous_files = len(media.files)
        media_file = add_new_media_file(media, url=url)
        # add_new_media_file will set media_file.media AND media.files.append
        # so we have two files for the media until the session is refreshed.
        DBSession.refresh(media)
        assert_length(previous_files+1, media.files)
        return media_file
    
    @data(*video_types)
    def test_can_detect_video_files(self, suffix):
        media = Media.example()
        assert_not_equals(VIDEO, media.type)
        self.add_external_file(media, suffix)
        media.update_status()
        assert_equals(VIDEO, media.type, message='did not detect %s as VIDEO type' % suffix)
    
    @data(*audio_types)
    def test_can_detect_audio_files(self, suffix):
        media = Media.example()
        assert_not_equals(AUDIO, media.type)
        self.add_external_file(media, suffix)
        media.update_status()
        assert_equals(AUDIO, media.type, message='did not detect %s as AUDIO type' % suffix)
    
    @data(*audio_types)
    def test_does_not_set_type_if_only_audio_description_files_are_attached(self, suffix):
        media = Media.example()
        assert_none(media.type)
        media_file = self.add_external_file(media, suffix)
        media_file.type = AUDIO_DESC
        media.update_status()
        assert_none(media.type, message='did detect media with audio description file as %s' % media.type)
    
    @data(*caption_types)
    def test_does_not_set_type_if_only_caption_files_are_attached(self, suffix):
        media = Media.example()
        assert_none(media.type)
        self.add_external_file(media, suffix)
        media.update_status()
        assert_none(media.type, message='did detect media with caption file as %s' % media.type)
    
    def test_sets_video_type_if_media_contains_audio_and_video_files(self):
        media = Media.example()
        assert_none(media.type)
        self.add_external_file(media, 'mp4')
        self.add_external_file(media, 'mp3')
        media.update_status()
        assert_equals(VIDEO, media.type, message='did not detect mixed video/audio media as VIDEO type')
        


import unittest
def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(MediaStatusUpdatesTypeTest))
    return suite

