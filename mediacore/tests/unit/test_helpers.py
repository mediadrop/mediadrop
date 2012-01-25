# This file is a part of MediaCore CE, Copyright 2009-2012 MediaCore Inc.
# The source code contained in this file is licensed under the GPL.
# See LICENSE.txt in the main project directory, for more information.

import pylons
from mediacore.tests import *
from mediacore.lib.compat import sha1
from mediacore.lib.players import pick_media_file_player
from mediacore.lib.mediafiles import add_new_media_file, save_media_obj
from mediacore.lib.thumbnails import thumb_path
from mediacore.lib.helpers import clean_xhtml, line_break_xhtml
from mediacore.model import DBSession
from sqlalchemy.exc import SQLAlchemyError

expected_text = "Expected:\n\"\"\"%s\"\"\"\n\nBut Got:\n\"\"\"%s\"\"\"\n"
results_text = "This:\n\"\"\"%s\"\"\"\n\nShould have been the same as:\n\"\"\"%s\"\"\"\n"

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

    def test_sizeless_file_picking(self):
        """Test while file gets served to each browser, given that all files
        are the same filesize.
        """
        media, media_files = self._get_media('unsized')

        for mf in media_files:
            media_files[mf].size = None
        DBSession.flush()

        pylons.app_globals.settings['html5_player'] = 'html5'
        pylons.app_globals.settings['flash_player'] = 'flowplayer'

        combinations = [
            # Prefer flash, without embeds
            ('firefox', 2,          'flash', False, 'flv', 'flowplayer'),
            ('firefox', 3,          'flash', False, 'flv', 'flowplayer'),
            ('firefox', 3.5,        'flash', False, 'flv', 'flowplayer'),
            ('safari', 522,         'flash', False, 'flv', 'flowplayer'),
            ('opera', 10.5,         'flash', False, 'flv', 'flowplayer'),
            ('opera', 9,            'flash', False, 'flv', 'flowplayer'),
            ('chrome', 3.0,         'flash', False, 'flv', 'flowplayer'),
            ('android', 0,          'flash', False, 'flv', 'flowplayer'),
            ('itunes', 0,           'flash', False, 'm4v', 'html5'),
            ('iphone-ipod-ipad', 0, 'flash', False, 'm4v', 'html5'),
            ('unknown', 0,          'flash', False, 'flv', 'flowplayer'),
            # Prefer flash, including embeds
            ('firefox', 2,          'flash', True, 'youtube', 'youtube'),
            ('firefox', 3,          'flash', True, 'youtube', 'youtube'),
            ('firefox', 3.5,        'flash', True, 'youtube', 'youtube'),
            ('safari', 522,         'flash', True, 'youtube', 'youtube'),
            ('opera', 10.5,         'flash', True, 'youtube', 'youtube'),
            ('opera', 9,            'flash', True, 'youtube', 'youtube'),
            ('chrome', 3.0,         'flash', True, 'youtube', 'youtube'),
            ('android', 0,          'flash', True, 'youtube', 'youtube'),
            ('itunes', 0,           'flash', True, 'm4v',     'html5'),
            ('iphone-ipod-ipad', 0, 'flash', True, 'm4v',     'html5'),
            ('unknown', 0,          'flash', True, 'youtube', 'youtube'),
            # Prefer HTML5, without embeds
            ('firefox', 2,          'best', False, 'flv', 'flowplayer'),
            ('firefox', 3,          'best', False, 'flv', 'flowplayer'),
            ('firefox', 3.5,        'best', False, 'ogv', 'html5'),
            ('safari', 522,         'best', False, 'm4v', 'html5'),
            ('opera', 10.5,         'best', False, 'ogv', 'html5'),
            ('opera', 9,            'best', False, 'flv', 'flowplayer'),
            ('chrome', 3.0,         'best', False, 'm4v', 'html5'),
            ('android', 0,          'best', False, 'm4v', 'html5'),
            ('itunes', 0,           'best', False, 'm4v', 'html5'),
            ('iphone-ipod-ipad', 0, 'best', False, 'm4v', 'html5'),
            ('unknown', 0,          'best', False, 'flv', 'flowplayer'),
            # Prefer HTML5, including embeds
            ('firefox', 2,          'best', True, 'youtube', 'youtube'),
            ('firefox', 3,          'best', True, 'youtube', 'youtube'),
            ('firefox', 3.5,        'best', True, 'ogv',     'html5'),
            ('safari', 522,         'best', True, 'm4v',     'html5'),
            ('opera', 10.5,         'best', True, 'ogv',     'html5'),
            ('opera', 9,            'best', True, 'youtube', 'youtube'),
            ('chrome', 3.0,         'best', True, 'm4v',     'html5'),
            ('android', 0,          'best', True, 'm4v',     'html5'),
            ('itunes', 0,           'best', True, 'm4v',     'html5'),
            ('iphone-ipod-ipad', 0, 'best', True, 'm4v',     'html5'),
            ('unknown', 0,          'best', True, 'youtube', 'youtube'),
            # HTML5 only, without embeds
            ('firefox', 2,          'html5', False, None,  None),
            ('firefox', 3,          'html5', False, None,  None),
            ('firefox', 3.5,        'html5', False, 'ogv', 'html5'),
            ('safari', 522,         'html5', False, 'm4v', 'html5'),
            ('opera', 10.5,         'html5', False, 'ogv', 'html5'),
            ('opera', 9,            'html5', False, None,  None),
            ('chrome', 3.0,         'html5', False, 'm4v', 'html5'),
            ('android', 0,          'html5', False, 'm4v', 'html5'),
            ('itunes', 0,           'html5', False, 'm4v', 'html5'),
            ('iphone-ipod-ipad', 0, 'html5', False, 'm4v', 'html5'),
            ('unknown', 0,          'html5', False, None, None),
            # HTML5 only, including embeds
            ('firefox', 2,          'html5', True, None,  None),
            ('firefox', 3,          'html5', True, None,  None),
            ('firefox', 3.5,        'html5', True, 'ogv', 'html5'),
            ('safari', 522,         'html5', True, 'm4v', 'html5'),
            ('opera', 10.5,         'html5', True, 'ogv', 'html5'),
            ('opera', 9,            'html5', True, None,  None),
            ('chrome', 3.0,         'html5', True, 'm4v', 'html5'),
            ('android', 0,          'html5', True, 'm4v', 'html5'),
            ('itunes', 0,           'html5', True, 'm4v', 'html5'),
            ('iphone-ipod-ipad', 0, 'html5', True, 'm4v', 'html5'),
            ('unknown', 0,          'html5', True, None, None),
        ]

        from mediacore.lib.players import players
        players = dict(players)
        players[None] = None
        media_files[None] = None

        for browser, version, p_type, embedded, e_file, e_player in combinations:
            player = pick_media_file_player(media,
                    browser = browser,
                    version = version,
                    player_type = p_type,
                    include_embedded = embedded
            )
            if player:
                file = player.file
                browser, version = player.browser
            else:
                file, browser, version = None, None, None
            print "Unsized:", browser, version, p_type, embedded, e_file, e_player
            player_class = player and player.__class__ or None
            assert player_class == players[e_player], "Expected %r but was %r" % (players[e_player], player_class)
            assert file == media_files[e_file], "Expected %r but got %r" % (media_files[e_file], file)

    def test_sized_file_picking(self):
        """Test while file gets served to each browser, given that all files are the same filesize.
        """
        media, media_files = self._get_media('sized')

        media_files['youtube'].size = None
        media_files['flv'].size = 500
        media_files['oga'].size = 1000
        media_files['ogv'].size = 2000
        media_files['m4a'].size = 3000
        media_files['m4v'].size = 4000
        media_files['mp3'].size = 5000
        media_files['xml'].size = 6000

        pylons.app_globals.settings['html5_player'] = 'html5'
        pylons.app_globals.settings['flash_player'] = 'flowplayer'

        combinations = [
            # Prefer flash, without embeds
            # TODO: write tests to check fallback players, and JW html5 player.
            ('firefox', 2,          'flash', False, 'm4v', 'flowplayer'),
            ('firefox', 3,          'flash', False, 'm4v', 'flowplayer'),
            ('firefox', 3.5,        'flash', False, 'm4v', 'flowplayer'),
            ('safari', 522,         'flash', False, 'm4v', 'flowplayer'),
            ('opera', 10.5,         'flash', False, 'm4v', 'flowplayer'),
            ('opera', 9,            'flash', False, 'm4v', 'flowplayer'),
            ('chrome', 3.0,         'flash', False, 'm4v', 'flowplayer'),
            ('android', 0,          'flash', False, 'm4v', 'flowplayer'),
            ('itunes', 0,           'flash', False, 'm4v', 'html5'),
            ('iphone-ipod-ipad', 0, 'flash', False, 'm4v', 'html5'),
            ('unknown', 0,          'flash', False, 'm4v', 'flowplayer'),
            # Prefer flash, including embeds
            ('firefox', 2,          'flash', True, 'youtube', 'youtube'),
            ('firefox', 3,          'flash', True, 'youtube', 'youtube'),
            ('firefox', 3.5,        'flash', True, 'youtube', 'youtube'),
            ('safari', 522,         'flash', True, 'youtube', 'youtube'),
            ('opera', 10.5,         'flash', True, 'youtube', 'youtube'),
            ('opera', 9,            'flash', True, 'youtube', 'youtube'),
            ('chrome', 3.0,         'flash', True, 'youtube', 'youtube'),
            ('android', 0,          'flash', True, 'youtube', 'youtube'),
            ('itunes', 0,           'flash', True, 'm4v',     'html5'),
            ('iphone-ipod-ipad', 0, 'flash', True, 'm4v',     'html5'),
            ('unknown', 0,          'flash', True, 'youtube', 'youtube'),
            # Prefer HTML5, without embeds
            ('firefox', 2,          'best', False, 'm4v', 'flowplayer'),
            ('firefox', 3,          'best', False, 'm4v', 'flowplayer'),
            ('firefox', 3.5,        'best', False, 'ogv', 'html5'),
            ('safari', 522,         'best', False, 'm4v', 'html5'),
            ('opera', 10.5,         'best', False, 'ogv', 'html5'),
            ('opera', 9,            'best', False, 'm4v', 'flowplayer'),
            ('chrome', 3.0,         'best', False, 'm4v', 'html5'),
            ('android', 0,          'best', False, 'm4v', 'html5'),
            ('itunes', 0,           'best', False, 'm4v', 'html5'),
            ('iphone-ipod-ipad', 0, 'best', False, 'm4v', 'html5'),
            ('unknown', 0,          'best', False, 'm4v', 'flowplayer'),
            # Prefer HTML5, including embeds
            ('firefox', 2,          'best', True, 'youtube', 'youtube'),
            ('firefox', 3,          'best', True, 'youtube', 'youtube'),
            ('firefox', 3.5,        'best', True, 'ogv',     'html5'),
            ('safari', 522,         'best', True, 'm4v',     'html5'),
            ('opera', 10.5,         'best', True, 'ogv',     'html5'),
            ('opera', 9,            'best', True, 'youtube', 'youtube'),
            ('chrome', 3.0,         'best', True, 'm4v',     'html5'),
            ('android', 0,          'best', True, 'm4v',     'html5'),
            ('itunes', 0,           'best', True, 'm4v',     'html5'),
            ('iphone-ipod-ipad', 0, 'best', True, 'm4v',     'html5'),
            ('unknown', 0,          'best', True, 'youtube', 'youtube'),
            # HTML5 only, without embeds
            ('firefox', 2,          'html5', False, None,  None),
            ('firefox', 3,          'html5', False, None,  None),
            ('firefox', 3.5,        'html5', False, 'ogv', 'html5'),
            ('safari', 522,         'html5', False, 'm4v', 'html5'),
            ('opera', 10.5,         'html5', False, 'ogv', 'html5'),
            ('opera', 9,            'html5', False, None,  None),
            ('chrome', 3.0,         'html5', False, 'm4v', 'html5'),
            ('android', 0,          'html5', False, 'm4v', 'html5'),
            ('itunes', 0,           'html5', False, 'm4v', 'html5'),
            ('iphone-ipod-ipad', 0, 'html5', False, 'm4v', 'html5'),
            ('unknown', 0,          'html5', False, None, None),
            # HTML5 only, including embeds
            ('firefox', 2,          'html5', True, None,  None),
            ('firefox', 3,          'html5', True, None,  None),
            ('firefox', 3.5,        'html5', True, 'ogv', 'html5'),
            ('safari', 522,         'html5', True, 'm4v', 'html5'),
            ('opera', 10.5,         'html5', True, 'ogv', 'html5'),
            ('opera', 9,            'html5', True, None,  None),
            ('chrome', 3.0,         'html5', True, 'm4v', 'html5'),
            ('android', 0,          'html5', True, 'm4v', 'html5'),
            ('itunes', 0,           'html5', True, 'm4v', 'html5'),
            ('iphone-ipod-ipad', 0, 'html5', True, 'm4v', 'html5'),
            ('unknown', 0,          'html5', True, None, None),
        ]

        from mediacore.lib.players import players
        players = dict(players)
        players[None] = None
        media_files[None] = None

        for browser, version, p_type, embedded, e_file, e_player in combinations:
            player = pick_media_file_player(media,
                    browser = browser,
                    version = version,
                    player_type = p_type,
                    include_embedded = embedded
            )
            if player:
                file = player.file
                browser, version = player.browser
            else:
                file, browser, version = None, None, None
            print "Sized:", browser, version, p_type, embedded, e_file, e_player
            player_class = player and player.__class__ or None
            assert player_class == players[e_player], "Expected %r but was %r" % (players[e_player], player_class)
            assert file == media_files[e_file], "Expected %r but got %r" % (media_files[e_file], file)

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
