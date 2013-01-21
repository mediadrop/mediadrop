# This file is a part of MediaCore CE (http://www.mediacorecommunity.org),
# Copyright 2009-2012 MediaCore Inc., Felix Schwarz and other contributors.
# For the exact contribution history, see the git revision log.
# The source code contained in this file is licensed under the GPLv3 or
# (at your option) any later version.
# See LICENSE.txt in the main project directory, for more information.

import pylons
from mediacore.tests import *
from mediacore.lib.compat import sha1
from mediacore.lib.storage import add_new_media_file
from mediacore.lib.thumbnails import thumb_path
from mediacore.lib.helpers import clean_xhtml, line_break_xhtml
from mediacore.model import Author, DBSession, Media
from sqlalchemy.exc import SQLAlchemyError

expected_text = "Expected:\n\"\"\"%s\"\"\"\n\nBut Got:\n\"\"\"%s\"\"\"\n"
results_text = "This:\n\"\"\"%s\"\"\"\n\nShould have been the same as:\n\"\"\"%s\"\"\"\n"


def save_media_obj(author_name, author_email, title, description, tags, file, url):
    media = Media()
    media.author = Author(author_name, author_email)
    media.title = title
    media.description = description
    media.tags = tags
    add_new_media_file(media, file=file, url=url)
    DBSession.add(media)
    DBSession.commit()
    return media

class TestHelpers(TestController):
    def __init__(self, *args, **kwargs):
        TestController.__init__(self, *args, **kwargs)

        # Initialize pylons.app_globals, for use in main thread.
        self.response = self.app.get('/_test_vars')
        pylons.app_globals._push_object(self.response.app_globals)

    def _get_media(self, unique):
        """Return the media/mediafiles required for the Helpers tests"""
        try:
            media = self._new_publishable_media(u'media-selection-%s' % unique,
                    u'Media Selection Test (%s)' % unique)
            DBSession.add(media)

            media_files = {}
            for t in ['oga', 'ogv', 'm4a', 'm4v', 'flv', 'mp3', 'xml']:
                media_files[t] = add_new_media_file(media, None,
                    u'http://fakesite.com/fakefile.%s' % t)
            media_files['youtube'] = add_new_media_file(media, None,
                    u'http://www.youtube.com/watch?v=3RsbmjNLQkc')
            media.update_status()
            DBSession.commit()
        except SQLAlchemyError, e:
            DBSession.rollback()
            raise e

        return media, media_files

    def test_add_youtube_video(self):
        pylons.app_globals.settings['use_embed_thumbnails'] = 'true'
        media = save_media_obj(
            u'Fake Name',
            u'fake@email.com',
            u'Old Spice',
            u'Isiah Mustafa stars in...',
            u'',
            None,
            u'http://www.youtube.com/watch?v=uLTIowBF0kE'
        )
        # XXX: The following values are based on the values provided by the
        #      remote site at the time this test was written. They may change
        #      in future.
        assert media.duration == 32
        thumbnail_path = thumb_path(media, 's', exists=True)
        assert thumbnail_path is not None
        img = open(thumbnail_path)
        s = sha1(img.read()).hexdigest()
        img.close()
        assert s == 'f0a3f5991fa032077faf2d3c698a6cf3e9dcadc1'

    def test_add_google_video(self):
        pylons.app_globals.settings['use_embed_thumbnails'] = 'true'
        media = save_media_obj(
            u'Fake Name',
            u'fake@email.com',
            u'Pictures at an Exhibition',
            u'A nice, long, production of the orchestrated Pictures...',
            u'',
            None,
            u'http://video.google.com/videoplay?docid=8997593004077118819'
        )
        # XXX: The following values are based on the values provided by the
        #      remote site at the time this test was written. They may change
        #      in future.
        assert media.duration == 1121
        thumbnail_path = thumb_path(media, 's', exists=True)
        assert thumbnail_path is not None
        img = open(thumbnail_path)
        s = sha1(img.read()).hexdigest()
        img.close()
        assert s == 'f8e84e4a487c9ff6ea69ac696c199ae6ac222e38'

    def test_add_vimeo_video(self):
        pylons.app_globals.settings['use_embed_thumbnails'] = 'true'
        media = save_media_obj(
            u'Fake Name',
            u'fake@email.com',
            u'Python Code Swarm',
            u'A visualization of all activity in the Python repository.',
            u'',
            None,
            u'http://www.vimeo.com/1093745'
        )
        # XXX: The following values are based on the values provided by the
        #      remote site at the time this test was written. They may change
        #      in future.
        assert media.duration == 282
        thumbnail_path = thumb_path(media, 's', exists=True)
        assert thumbnail_path is not None
        img = open(thumbnail_path)
        s = sha1(img.read()).hexdigest()
        img.close()
        assert s == '1eb9442b7864841e0f48270de7e3e871050b3876'

    def test_clean_xhtml_linebreaks(self):
        expected_clean = "<p>First line first line cont'd</p><p>second line</p><p>third line</p><p>fourth line</p>"
        dirty = """First line\nfirst line cont'd\n\nsecond line\n\nthird line\n\n\n\nfourth line"""
        # Ensure that the cleaned XHTML is what we expected
        clean = clean_xhtml(dirty)
        assert clean == expected_clean, expected_text % (expected_clean, clean)
        # Ensure that re-cleaning the XHTML provides the same result.
        clean = clean_xhtml(clean)
        assert clean == expected_clean, expected_text % (expected_clean, clean)

    def test_clean_xhtml_mixed1(self):
        expected_clean = "<p>First line first line cont'd.</p><p>second line</p><p>third line</p>"
        dirty = """<p>First line\nfirst line cont'd.\n\nsecond line</p>\nthird line\n\n"""
        # Ensure that the cleaned XHTML is what we expected
        clean = clean_xhtml(dirty)
        assert clean == expected_clean, expected_text % (expected_clean, clean)
        # Ensure that re-cleaning the XHTML provides the same result.
        clean = clean_xhtml(clean)
        assert clean == expected_clean, expected_text % (expected_clean, clean)

    def test_clean_xhtml_mixed2(self):
        expected_clean = "<p>First line first line cont'd.</p><p>second line</p><p>third line</p>"
        dirty1 = """<p>First line\nfirst line cont'd.\n\nsecond line</p>\nthird line\n"""
        dirty2 = """<p>First line\nfirst line cont'd.\n\nsecond line</p>\nthird line\n\n"""
        # Ensure that the cleaned XHTML is the same regardless of trailing newlines.
        clean1 = clean_xhtml(dirty1)
        clean2 = clean_xhtml(dirty2)
        assert clean1 == clean2, results_text % (clean1, clean2)

    def test_xhtmltextarea_logic(self):
        """Mimics the input -> clean -> display -> input... cycle of the XHTMLTextArea widget."""
        expected_clean = "<p>First line first line cont'd</p><p>second line</p><p>third line</p><p>fourth line</p>"
        dirty = "First line\nfirst line cont'd\n\nsecond line\n\nthird line\n\n\n\nfourth line"
        # Ensure that the cleaned XHTML is what we expected
        clean = clean_xhtml(dirty)
        assert clean == expected_clean, expected_text % (expected_clean, clean)
        # Ensure that re-cleaning the XHTML provides the same result.
        displayed = line_break_xhtml(clean)
        clean = clean_xhtml(displayed)
        assert clean == expected_clean, expected_text % (expected_clean, clean)
