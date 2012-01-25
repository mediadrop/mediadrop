# This file is a part of MediaCore CE, Copyright 2009-2012 MediaCore Inc.
# The source code contained in this file is licensed under the GPL.
# See LICENSE.txt in the main project directory, for more information.

from mediacore.tests import *
from mediacore.model import DBSession, Media, fetch_row

class TestUploadController(TestController):

    def test_index(self):
        response = self.app.get(url(controller='upload', action='index'))
        # Test response...

    def _valid_values(self, title):
        fields = dict(
            name = 'Frederick Awesomeson',
            email = 'fake_address@mailinator.com',
            title = title,
            description = 'actually just testing an mp3 upload.',
            url = '',
        )
        files = [
            ('file', '/some/fake/filename.mp3', 'FILE CONTENT: This is not an MP3 file at all, but this random string will work for our purposes.')
        ]
        return fields, files

    def test_submit_async(self):
        fields, files = self._valid_values('testing mp3 async upload')
        submit_url = url(controller='upload', action='submit_async')
        success_url = url(controller='upload', action='success')

        response = self.app.post(submit_url, params=fields, upload_files=files)
        assert response.status_int == 200
        assert response.headers['Content-Type'] == 'application/json'
        assert response.body == '{"redirect": "/upload/success", "success": true}'

        media = fetch_row(Media, slug=u'testing-mp3-async-upload')
        assert len(media.files) == 1
        assert media.files[0].container == 'mp3'
        assert media.description == "<p>actually just testing an mp3 upload.</p>"

    def test_submit(self):
        fields, files = self._valid_values('testing mp3 upload')
        index_url = url(controller='upload', action='index')
        submit_url = url(controller='upload', action='submit')
        success_url = url(controller='upload', action='success')

        index_response = self.app.get(index_url, status=200)

        # Ensure that the form has the correct action and fields
        form = index_response.forms['upload-form']
        for x in fields:
            form[x] = fields[x]
        assert form.action == submit_url

        # Submit the form with a regular POST request anyway, because
        # webtest.Form objects can't handle file uploads.
        submit_response = self.app.post(submit_url, params=fields, upload_files=files)
        assert submit_response.status_int == 302
        assert submit_response.location == 'http://localhost%s' % success_url

        # Ensure the media item and file were  created properly.
        media = fetch_row(Media, slug=u'testing-mp3-upload')
        assert len(media.files) == 1
        assert media.files[0].container == 'mp3'
        assert media.description == "<p>actually just testing an mp3 upload.</p>"
