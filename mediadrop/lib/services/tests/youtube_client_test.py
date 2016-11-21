# -*- coding: utf-8 -*-
# This file is a part of MediaDrop (http://www.mediadrop.video),
# Copyright 2009-2015 MediaDrop contributors
# For the exact contribution history, see the git revision log.
# The source code contained in this file is licensed under the GPLv3 or
# (at your option) any later version.
# See LICENSE.txt in the main project directory, for more information.

from apiclient.errors import HttpError
import simplejson as json

from mediadrop.lib.attribute_dict import AttrDict
from mediadrop.lib.filetypes import VIDEO
from mediadrop.lib.i18n import setup_global_translator
from mediadrop.lib.services.youtube import YouTubeClient
from mediadrop.lib.test import DBTestCase
from mediadrop.lib.test.pythonic_testcase import *


class YoutubeClientTest(DBTestCase):
    def setUp(self):
        super(YoutubeClientTest, self).setUp()
        # error messages need a registered translator
        paste_registry = self.pylons_config['paste.registry']
        setup_global_translator(registry=paste_registry)

    def mock_client(self, video_id='BZLYoDpPQwcj', duration='PT30S', title='foo', description='bar', expected_parts=''):
        video_data = {
            'items': [{
                'contentDetails': {
                    'duration': duration,
                },
                'id': video_id,
                'snippet': {
                    'title': title,
                    'description': description,
                    'thumbnails': {
                        'lowbaz': {
                            'height': 90,
                            'width': 120,
                            'url': 'https://i.ytimg.com/vi/%s/default.jpg' % video_id,
                        },
                        'highbar': {
                            'height': 480,
                            'width': 640,
                            'url': 'https://i.ytimg.com/vi/%s/sddefault.jpg' % video_id,
                        },
                    }
                }
            }]
        }
        return self._build_client_instance(video_id, expected_parts, video_data)

    def _build_client_instance(self, expected_video_id, expected_parts, video_data_response=None, error=None):
        def fake_query(id=None, part=None):
            assert_equals(id, expected_video_id, message='attempted to retrieve unexpected video %s' % id)
            assert_equals(part, expected_parts, message='unexpected parts')
            if video_data_response:
                return AttrDict(execute=lambda: video_data_response)
            data = {'error': {'errors': [error]}}
            error_content = json.dumps(data)
            exception = HttpError('dummy', error_content)
            def raising_execute():
                raise exception
            return AttrDict(execute=raising_execute)
        fake_yt = AttrDict(
            videos=lambda: AttrDict(list=fake_query),
        )
        return YouTubeClient(fake_yt)

    def test_can_handle_invalid_youtube_id(self):
        video_id = 'invalid'
        youtube_client = self._build_client_instance(
            video_id,
            'snippet,contentDetails',
            {'items': []}
        )
        result = youtube_client.fetch_video_details(video_id)
        assert_false(result)

    def test_can_handle_invalid_api_key(self):
        video_id = 'AQTYoRpCXwg'
        youtube_client = self._build_client_instance(
            video_id,
            'snippet,contentDetails',
            error={'code': 400, 'reason': 'keyInvalid', 'message': 'bar'}
        )
        result = youtube_client.fetch_video_details(video_id)
        assert_false(result)
        assert_contains('Invalid API key', result.message)

    def test_can_handle_api_key_without_youtube_access(self):
        video_id = 'AQTYoRpCXwg'
        youtube_client = self._build_client_instance(
            video_id,
            'snippet,contentDetails',
            error={'code': 403, 'reason': 'accessNotConfigured',
                   'message': 'The API (YouTube Data API) is not enabled for your project.'}
        )
        result = youtube_client.fetch_video_details(video_id)
        assert_false(result)
        assert_contains(
            'The API (YouTube Data API) is not enabled for your project.',
            result.message
        )

    def test_can_fetch_video_details(self):
        video_id = 'AQTYoRpCXwg'
        youtube_client = self.mock_client(
            video_id=video_id,
            duration='PT2M10S',
            title='Puppies and Cats',
            description='everyone loves kittens',
            expected_parts='snippet,contentDetails',
        )
        result = youtube_client.fetch_video_details(video_id)
        assert_true(result)

        meta = AttrDict(result.meta_info)
        assert_equals(video_id, meta.unique_id)
        assert_equals(130, meta.duration)
        assert_equals('Puppies and Cats', meta.display_name)
        assert_equals('everyone loves kittens', meta.description)
        expected_thumb = {
            'width': 640,
            'height': 480,
            'url': 'https://i.ytimg.com/vi/%s/sddefault.jpg' % video_id,
        }
        assert_equals(expected_thumb, meta.thumbnail)
        assert_equals(VIDEO, meta.type)



import unittest

def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(YoutubeClientTest))
    return suite
    
if __name__ == '__main__':
    unittest.main(defaultTest='suite')
