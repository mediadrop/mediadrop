from mediacore.tests import *

class TestMediaApiController(TestController):

    def test_index(self):
        response = self.app.get(url(controller='media_api', action='index'))
        # Test response...
