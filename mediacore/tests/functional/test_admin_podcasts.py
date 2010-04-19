from mediacore.tests import *

class TestPodcastsController(TestController):

    def test_index(self):
        response = self.app.get(url(controller='admin/podcasts', action='index'))
        # Test response...
