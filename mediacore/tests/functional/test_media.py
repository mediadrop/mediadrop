from mediacore.tests import *

class TestMediaController(TestController):

    def test_index(self):
        response = self.app.get(url(controller='media', action='index'))
        # Test response...
