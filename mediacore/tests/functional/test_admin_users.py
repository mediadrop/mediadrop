from mediacore.tests import *

class TestUsersController(TestController):

    def test_index(self):
        response = self.app.get(url(controller='admin/users', action='index'))
        # Test response...
