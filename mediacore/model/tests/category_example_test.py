
from mediacore.lib.test.db_testcase import DBTestCase
from mediacore.lib.test.pythonic_testcase import *
from mediacore.model import Category


class CategoryExampleTest(DBTestCase):
    def test_can_create_example_category(self):
        category = Category.example()
        assert_not_none(category)
        assert_equals(u'Foo', category.name)
        assert_equals(u'foo', category.slug)
        assert_equals(0, category.parent_id)

    def test_can_override_example_data(self):
        category = Category.example(name=u'Bar')
        assert_equals(u'Bar', category.name)
        assert_equals(u'bar', category.slug)

    def test_can_override_only_existing_attributes(self):
        # should raise AssertionError
        assert_raises(AssertionError, lambda: Category.example(foo=u'bar'))


import unittest
def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(CategoryExampleTest))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='suite')
