from mediacore.tests import *

class TestPodcastsController(TestController):

    def test_index(self):
        response = self.app.get(url(controller='podcasts', action='index'))
        # Test response...
