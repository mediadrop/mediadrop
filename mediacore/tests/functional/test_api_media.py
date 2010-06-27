from mediacore.tests import *

class TestApiMediaController(TestController):

    def test_index(self):
        response = self.app.get(url(controller='api/media', action='index'))
        # Test response...
