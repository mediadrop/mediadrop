# This file is a part of MediaDrop (http://www.mediadrop.net),
# Copyright 2009-2013 MediaCore Inc., Felix Schwarz and other contributors.
# For the exact contribution history, see the git revision log.
# The source code contained in this file is licensed under the GPLv3 or
# (at your option) any later version.
# See LICENSE.txt in the main project directory, for more information.

import pylons
from mediacore.tests import *
from mediacore.lib.filetypes import AUDIO, AUDIO_DESC, CAPTIONS, VIDEO
from mediacore.lib.storage import add_new_media_file
from mediacore.model import DBSession
from sqlalchemy.exc import SQLAlchemyError

class TestModels(TestController):

    audio_types = [u'mp3', u'm4a', u'flac', u'oga', u'mka']
    video_types = [u'mp4', u'm4v', u'ogg', u'ogv', u'mkv', u'3gp', u'webm', u'avi',
                   u'dv', u'flv', u'mov', u'mpeg', u'mpg', u'wmv']
    caption_types = [u'xml', u'srt']

    def __init__(self, *args, **kwargs):
        TestController.__init__(self, *args, **kwargs)

        # Initialize pylons.app_globals, for use in main thread.
        self.response = self.app.get('/_test_vars')
        pylons.app_globals._push_object(self.response.app_globals)

    def test_audio_url_media(self):
        """Media with only audio files attatched should be AUDIO type."""
        try:
            for t in self.audio_types:
                media = self._new_publishable_media(u'audio-%s' % t,
                        u'%s (Audio)' % t.upper())
                DBSession.add(media)
                media_file = add_new_media_file(media, None,
                        u'http://fakesite.com/fakefile.%s' % t)
                media.update_status()
                DBSession.commit()
                assert media.type == AUDIO, \
                    "A Media object with only an .%s file associated was " \
                    "not labelled as an audio type; it was labelled %s" % \
                    (t, media.type)
        except SQLAlchemyError, e:
            DBSession.rollback()
            raise e

    def test_video_url_media(self):
        """Media with only video files attatched should be VIDEO type."""
        try:
            for t in self.video_types:
                media = self._new_publishable_media(u'video-%s' % t,
                        u'%s (Video)' % t.upper())
                DBSession.add(media)
                media_file = add_new_media_file(media, None,
                        u'http://fakesite.com/fakefile.%s' % t)
                media.update_status()
                DBSession.commit()
                assert media.type == VIDEO, \
                    "A Media object with only an .%s file associated was " \
                    "not labelled as a video type; it was labelled %s" % \
                    (t, media.type)
        except SQLAlchemyError, e:
            DBSession.rollback()
            raise e

    def test_captioned_url_media(self):
        """Media with only subtitles attatched should be None type."""
        try:
            for t in self.caption_types:
                media = self._new_publishable_media(u'caption-%s' % t,
                        u'%s (Captioned)' % t.upper())
                DBSession.add(media)
                media_file = add_new_media_file(media, None,
                        u'http://fakesite.com/fakefile.%s' % t)
                media.update_status()
                DBSession.commit()
                assert media.type == None, \
                    "A Media object with only an .%s file associated was " \
                    "not labelled as a 'None' type; it was labelled %s" % \
                    (t, media.type)
        except SQLAlchemyError, e:
            DBSession.rollback()
            raise e

    def test_audio_description_url_media(self):
        """Media with only Audio Descriptions attatched should be None type."""
        try:
            for t in self.audio_types:
                media = self._new_publishable_media(u'description-%s' % t,
                        u'%s (Audio Description)' % t.upper())
                DBSession.add(media)
                media_file = add_new_media_file(media, None,
                        u'http://fakesite.com/fakefile.%s' % t)
                media_file.type = AUDIO_DESC
                media.update_status()
                DBSession.commit()
                assert media.type == None, \
                    "A Media object with only an Audio Description file " \
                    "associated was not labelled as a None type; it " \
                    "was labelled %s" % (t, media.type)
        except SQLAlchemyError, e:
            DBSession.rollback()
            raise e

    def test_audio_video_url_media(self):
        """Media with both Audio files and Video files attatched should be
        Video type."""
        try:
            # Create the media object
            media = self._new_publishable_media(u'audio-video',
                    u'(Audio + Video)')
            DBSession.add(media)
            # Add an audio description
            media_file = add_new_media_file(media, None,
                    u'http://fakesite.com/fakefile.mp3')
            media.update_status()
            # Add a video file
            media_file = add_new_media_file(media, None,
                    u'http://fakesite.com/fakefile.m4v')
            media.update_status()
            # Commit + test
            DBSession.commit()
            assert media.type == VIDEO, \
                "A Media object with a .m4v file and an audio file " \
                "was not labelled as a video type; it was labelled %s" % \
                (t, media.type)
        except SQLAlchemyError, e:
            DBSession.rollback()
            raise e

    def test_audiodesc_video_url_media(self):
        """Media with both Audio files and Video files attatched should be
        Video type."""
        try:
            # Create the media object
            media = self._new_publishable_media(u'description-video',
                    u'(Audio Description + Video)')
            DBSession.add(media)
            # Add an audio description
            media_file = add_new_media_file(media, None,
                    u'http://fakesite.com/fakefile.mp3')
            media_file.type = AUDIO_DESC
            media.update_status()
            # Add a video file
            media_file = add_new_media_file(media, None,
                    u'http://fakesite.com/fakefile.m4v')
            media.update_status()
            # Commit + test
            DBSession.commit()
            assert media.type == VIDEO, \
                "A Media object with a .m4v file and an Audio Description " \
                "was not labelled as a video type; it was labelled %s" % \
                (t, media.type)
        except SQLAlchemyError, e:
            DBSession.rollback()
            raise e
