# This file is a part of MediaDrop (http://www.mediadrop.net),
# Copyright 2009-2013 MediaDrop contributors
# For the exact contribution history, see the git revision log.
# The source code contained in this file is licensed under the GPLv3 or
# (at your option) any later version.
# See LICENSE.txt in the main project directory, for more information.

from mediadrop.model import DBSession, Media
from mediadrop.lib.filetypes import VIDEO
from mediadrop.lib.players import AbstractFlashPlayer, FlowPlayer
from mediadrop.lib.storage.api import add_new_media_file
from mediadrop.lib.test.db_testcase import DBTestCase
from mediadrop.lib.test.pythonic_testcase import *
from mediadrop.plugin import events
from mediadrop.plugin.events import observes


class MediaTest(DBTestCase):
    def setUp(self):
        super(MediaTest, self).setUp()
        self.init_flowplayer()
        self.media = Media.example()
        self.encoding_event = self.create_spy_on_event(events.Media.encoding_done)
    
    def init_flowplayer(self):
        AbstractFlashPlayer.register(FlowPlayer)
        FlowPlayer.inject_in_db(enable_player=True)
    
    def create_spy_on_event(self, event):
        encoding_event = create_spy()
        observes(event)(encoding_event)
        return encoding_event
    
    def add_external_file(self, media, url=u'http://site.example/videos.mp4'):
        previous_files = len(media.files)
        media_file = add_new_media_file(media, url=url)
        # add_new_media_file will set media_file.media AND media.files.append
        # so we have two files for the media until the session is refreshed.
        DBSession.refresh(media)
        assert_length(previous_files+1, media.files)
        return media_file
    
    def test_can_update_status(self):
        assert_false(self.media.encoded)
        
        self.media.update_status()
        assert_false(self.media.encoded)
        self.encoding_event.assert_was_not_called()
    
    def test_triggers_event_when_media_was_encoded(self):
        self.add_external_file(self.media)
        assert_false(self.media.encoded)
        self.media.update_status()
        
        assert_equals(VIDEO, self.media.type)
        assert_true(self.media.encoded)
        self.encoding_event.assert_was_called_with(self.media)
        
        # only send event when the encoding status changes!
        second_encoding_event = self.create_spy_on_event(events.Media.encoding_done)
        self.media.update_status()
        second_encoding_event.assert_was_not_called()


import unittest
def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(MediaTest))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='suite')
