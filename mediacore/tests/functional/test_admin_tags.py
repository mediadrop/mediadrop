from mediacore.tests import *

class TestTagsController(TestController):

    def test_index(self):
        response = self.app.get(url(controller='admin/tags', action='index'))
        # Test response...
