from mediacore.tests import *

class TestSettingsController(TestController):

    def test_index(self):
        response = self.app.get(url(controller='admin/settings', action='index'))
        # Test response...
