# This file is a part of MediaDrop (http://www.mediadrop.net),
# Copyright 2009-2013 MediaDrop contributors
# For the exact contribution history, see the git revision log.
# The source code contained in this file is licensed under the GPLv3 or
# (at your option) any later version.
# See LICENSE.txt in the main project directory, for more information.

from mediadrop.model import Author, Media
from mediadrop.lib.test.db_testcase import DBTestCase
from mediadrop.lib.test.pythonic_testcase import *



class MediaExampleTest(DBTestCase):
    def test_can_create_example_media(self):
        media = Media.example()
        
        assert_not_none(media.id)
        assert_equals(u'Foo Media', media.title)
        assert_equals(u'foo-media', media.slug)
        assert_equals(Author(u'Joe', u'joe@site.example'), media.author)
        assert_length(0, media.files)
        
        assert_none(media.type)
        assert_none(media.podcast_id)
        
        assert_false(media.publishable)
        assert_false(media.reviewed)
        assert_false(media.encoded)
        assert_none(media.publish_on)
        assert_none(media.publish_until)
        assert_false(media.is_published)
    
    def test_can_override_example_data(self):
        media = Media.example(title=u'Bar Foo')
        
        assert_equals(u'Bar Foo', media.title)
        assert_equals(u'bar-foo', media.slug)


import unittest
def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(MediaExampleTest))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='suite')
