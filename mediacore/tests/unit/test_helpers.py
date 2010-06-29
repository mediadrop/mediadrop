import pylons
from mediacore.tests import *
from mediacore.lib.filetypes import pick_media_file_player
from mediacore.lib.mediafiles import add_new_media_file
from mediacore.model import DBSession
from sqlalchemy.exc import SQLAlchemyError

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
                    'http://fakesite.com/fakefile.%s' % t)
            media_files['youtube'] = add_new_media_file(media, None,
                    'http://www.youtube.com/watch?v=3RsbmjNLQkc')
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

        from mediacore.lib.helpers import players
        players = dict(players)
        players[None] = None
        media_files[None] = None

        for browser, version, p_type, embedded, e_file, e_player in combinations:
            file, player, browser, version = pick_media_file_player(media.files,
                    browser = browser,
                    version = version,
                    player_type = p_type,
                    include_embedded = embedded
            )
            print "Unsized:", browser, version, p_type, embedded, e_file, e_player
            assert player == players[e_player], "Expected %r but was %r" % (players[e_player], player)
            assert file == media_files[e_file], "Expected %r but got %r" % (media_files[e_file], file)

