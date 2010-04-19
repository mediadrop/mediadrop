from mediacore.tests import *

class TestCommentsController(TestController):

    def test_index(self):
        response = self.app.get(url(controller='admin/comments', action='index'))
        # Test response...
