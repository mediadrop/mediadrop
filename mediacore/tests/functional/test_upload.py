from mediacore.tests import *

class TestUploadController(TestController):

    def test_index(self):
        response = self.app.get(url(controller='upload', action='index'))
        # Test response...
