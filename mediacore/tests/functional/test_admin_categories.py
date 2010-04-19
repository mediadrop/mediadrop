from mediacore.tests import *

class TestCategoriesController(TestController):

    def test_index(self):
        response = self.app.get(url(controller='admin/categories', action='index'))
        # Test response...
