import pylons
from datetime import datetime
from mediacore.tests import *
from mediacore.model import Author, Category, DBSession, Media
from mediacore.lib.filetypes import AUDIO, AUDIO_DESC, CAPTIONS, VIDEO
from mediacore.lib.mediafiles import add_new_media_file
from sqlalchemy.exc import SQLAlchemyError

class TestModels(TestController):

    audio_types = ['mp3', 'm4a', 'flac', 'oga', 'mka']
    video_types = ['mp4', 'm4v', 'ogg', 'ogv', 'mkv', '3gp', '3g2', 'avi',
                   'dv', 'flv', 'mov', 'mpeg', 'mpg', 'wmv']
    caption_types = ['xml', 'srt']

    def __init__(self, *args, **kwargs):
        TestController.__init__(self, *args, **kwargs)

        # Initialize pylons.app_globals, for use in main thread.
        self.response = self.app.get('/_test_vars')
        pylons.app_globals._push_object(self.response.app_globals)

    def _new_publishable_media(self, slug, name):
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

    def test_audio_url_media(self):
        """Media with only audio files attatched should be AUDIO type."""
        try:
            for t in self.audio_types:
                media = self._new_publishable_media(u'audio-%s' % t,
                        u'%s (Audio)' % t.upper())
                DBSession.add(media)
                media_file = add_new_media_file(media, None,
                        'http://fakesite.com/fakefile.%s' % t)
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
                        'http://fakesite.com/fakefile.%s' % t)
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
                        'http://fakesite.com/fakefile.%s' % t)
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
                        'http://fakesite.com/fakefile.%s' % t)
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
