import pylons
from datetime import datetime
from mediacore.tests import *
from mediacore.model import Author, Category, DBSession, Media
from mediacore.lib.mediafiles import generic_add_new_media_file

class TestModels(TestController):

    def __init__(self, *args, **kwargs):
        TestController.__init__(self, *args, **kwargs)

        # Initialize pylons.app_globals, for use in main thread.
        self.response = self.app.get('/_test_vars')
        pylons.app_globals._push_object(self.response.app_globals)

    def test_media(self):
        pass
