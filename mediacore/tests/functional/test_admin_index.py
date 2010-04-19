from mediacore.tests import *

class TestIndexController(TestController):

    def test_index(self):
        response = self.app.get(url(controller='admin/index', action='index'))
        # Test response...
