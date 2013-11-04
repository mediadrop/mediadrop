# This file is a part of MediaDrop (http://www.mediadrop.net),
# Copyright 2009-2013 MediaDrop contributors
# For the exact contribution history, see the git revision log.
# The source code contained in this file is licensed under the GPLv3 or
# (at your option) any later version.
# See LICENSE.txt in the main project directory, for more information.

import os
import pylons
import simplejson
import webob.exc
from mediadrop.tests import *
from mediadrop.model import DBSession, Media, MediaFile, fetch_row
from sqlalchemy.exc import SQLAlchemyError

class TestMediaController(TestController):
    def __init__(self, *args, **kwargs):
        TestController.__init__(self, *args, **kwargs)

        # Initialize pylons.app_globals, etc. for use in main thread.
        self.response = self.app.get('/_test_vars')
        pylons.app_globals._push_object(self.response.app_globals)
        pylons.config._push_object(self.response.config)

        # So that Pylons.url can generate fully qualified URLs.
        pylons.url.environ['SERVER_NAME'] = 'test_value'
        pylons.url.environ['SERVER_PORT'] = '80'

    def _login(self):
        test_user = 'admin'
        test_password = 'admin'
        login_form_url = url(controller='login', action='login')
        # Request, and fill out, the login form.
        login_page = self.app.get(login_form_url, status=200)
        login_page.form['login'] = test_user
        login_page.form['password'] = test_password
        # Submitting the login form should redirect us to the 'post_login' page
        login_handler_page = login_page.form.submit(status=302)

    def test_index(self):
        response = self.app.get(url(controller='admin/media', action='index'))
        # Test response...

    def test_add_new_media(self):
        new_url = url(controller='admin/media', action='edit', id='new')
        save_url = url(controller='admin/media', action='save', id='new')

        title = 'Add New Media Test'
        slug = u'add-new-media-test' # this should be unique
        name = 'Frederick Awesomeson'
        email = 'fake_address@mailinator.com'
        description = 'This media item was created to test the "admin/media/edit/new" method'
        htmlized_description = '<p>This media item was created to test the &quot;admin/media/edit/new&quot; method</p>'

        self._login()
        new_response = self.app.get(new_url, status=200)
        form = new_response.forms['media-form']
        form['title'] = title
        form['author_name'] = name
        form['author_email'] = email
        form['description'] = description
        # form['categories']
        # form['tags']
        form['notes'] = ''
        assert form.action == save_url

        save_response = form.submit()

        # Ensure that the correct redirect was issued
        assert save_response.status_int == 302
        media = fetch_row(Media, slug=slug)
        edit_url = url(controller='admin/media', action='edit', id=media.id)
        assert save_response.location == 'http://localhost%s' % edit_url

        # Ensure that the media object was correctly created
        assert media.title == title
        assert media.author.name == name
        assert media.author.email == email
        assert media.description == htmlized_description

        # Ensure that the edit form is correctly filled out
        edit_response = save_response.follow()
        form = edit_response.forms['media-form']
        assert form['title'].value == title
        assert form['author_name'].value == name
        assert form['author_email'].value == email
        assert form['slug'].value == slug
        assert form['description'].value == htmlized_description
        assert form['notes'].value == ''

    def test_edit_media(self):
        title = u'Edit Existing Media Test'
        slug = u'edit-existing-media-test' # this should be unique

        # Values that we will change during the edit process
        name = u'Frederick Awesomeson'
        email = u'fake_address@mailinator.com'
        description = u'This media item was created to test the "admin/media/edit/someID" method'
        htmlized_description = '<p>This media item was created to test the &quot;admin/media/edit/someID&quot; method</p>'
        notes = u'Some Notes!'

        try:
            media = self._new_publishable_media(slug, title)
            media.publishable = False
            media.reviewed = False
            DBSession.add(media)
            DBSession.commit()
            media_id = media.id
        except SQLAlchemyError, e:
            DBSession.rollback()
            raise e

        edit_url = url(controller='admin/media', action='edit', id=media_id)
        save_url = url(controller='admin/media', action='save', id=media_id)

        # render the edit form
        self._login()
        edit_response = self.app.get(edit_url, status=200)

        # ensure the form submits like we want it to
        form = edit_response.forms['media-form']
        assert form.action == save_url

        # Fill out the edit form, and submit it
        form['title'] = title
        form['author_name'] = name
        form['author_email'] = email
        form['description'] = description
        # form['categories']
        # form['tags']
        form['notes'] = notes
        save_response = form.submit()

        # Ensure that the correct redirect was issued
        assert save_response.status_int == 302
        assert save_response.location == 'http://localhost%s' % edit_url

        # Ensure that the media object was correctly updated
        media = fetch_row(Media, media_id)
        assert media.title == title
        assert media.slug == slug
        assert media.notes == notes
        assert media.description == htmlized_description
        assert media.author.name == name
        assert media.author.email == email

    def test_add_file(self):
        slug = u'test-add-file'
        title = u'Test Adding File on Media Edit Page.'

        try:
            media = self._new_publishable_media(slug, title)
            media.publishable = False
            media.reviewed = False
            DBSession.add(media)
            DBSession.commit()
            media_id = media.id
        except SQLAlchemyError, e:
            DBSession.rollback()
            raise e

        edit_url = url(controller='admin/media', action='edit', id=media_id)
        add_url = url(controller='admin/media', action='add_file', id=media_id)
        files = [
            ('file', '/some/fake/filename.mp3', 'FILE CONTENT: This is not an MP3 file at all, but this random string will work for our purposes.')
        ]
        fields = {
            'url': '',
        }
        # render the edit form
        self._login()
        edit_response = self.app.get(edit_url, status=200)

        # Ensure that the add-file-form rendered correctly.
        form = edit_response.forms['add-file-form']
        assert form.action == add_url
        for x in fields:
            form[x] = fields[x]
        form['file'] = files[0][1]

        # Submit the form with a regular POST request anyway, because
        # webtest.Form objects can't handle file uploads.
        add_response = self.app.post(add_url, params=fields, upload_files=files)
        assert add_response.status_int == 200
        assert add_response.headers['Content-Type'] == 'application/json'

        # Ensure the media file was created properly.
        media = fetch_row(Media, slug=slug)
        assert media.files[0].container == 'mp3'
        assert media.files[0].type == 'audio'
        assert media.type == 'audio'

        # Ensure that the response content was correct.
        add_json = simplejson.loads(add_response.body)
        assert add_json['success'] == True
        assert add_json['media_id'] == media_id
        assert add_json['file_id'] == media.files[0].id
        assert 'message' not in add_json

        # Ensure that the file was properly created.
        file_uri = [u for u in media_1.files[0].get_uris() if u.scheme == 'file'][0]
        file_name = file_uri.file_uri
        file_path = os.sep.join((pylons.config['media_dir'], file_name))
        assert os.path.exists(file_path)
        file = open(file_path)
        content = file.read()
        file.close()
        assert content == files[0][2]

    def test_add_file_url(self):
        slug = u'test-add-file-url'
        title = u'Test Adding File by URL on Media Edit Page.'

        try:
            media = self._new_publishable_media(slug, title)
            media.publishable = False
            media.reviewed = False
            DBSession.add(media)
            DBSession.commit()
            media_id = media.id
        except SQLAlchemyError, e:
            DBSession.rollback()
            raise e

        edit_url = url(controller='admin/media', action='edit', id=media_id)
        add_url = url(controller='admin/media', action='add_file', id=media_id)
        fields = {
            'url': 'http://www.youtube.com/watch?v=uLTIowBF0kE',
        }
        # render the edit form
        self._login()
        edit_response = self.app.get(edit_url, status=200)

        # Ensure that the add-file-form rendered correctly.
        form = edit_response.forms['add-file-form']
        assert form.action == add_url
        for x in fields:
            form[x] = fields[x]

        # Submit the form with a regular POST request anyway, because
        # webtest.Form objects can't handle file uploads.
        add_response = self.app.post(add_url, params=fields)
        assert add_response.status_int == 200
        assert add_response.headers['Content-Type'] == 'application/json'

        # Ensure the media file was created properly.
        media = fetch_row(Media, slug=slug)
        assert media.files[0].get_uris()[0].scheme == 'youtube'
        assert media.files[0].type == 'video'
        assert media.type == 'video'

        # Ensure that the response content was correct.
        add_json = simplejson.loads(add_response.body)
        assert add_json['success'] == True
        assert add_json['media_id'] == media_id
        assert add_json['file_id'] == media.files[0].id
        assert 'message' not in add_json

    def test_merge_stubs(self):
        new_url = url(controller='admin/media', action='edit', id='new')
        save_url = url(controller='admin/media', action='save', id='new')
        add_url = url(controller='admin/media', action='add_file', id='new')

        title = 'Merge Stubs Test'
        slug = u'merge-stubs-test' # this should be unique
        name = 'Frederick Awesomeson'
        email = 'fake_address@mailinator.com'
        description = 'This media item was created to test the "admin/media/merge_stubs" method'
        htmlized_description = '<p>This media item was created to test the &quot;admin/media/merge_stubs&quot; method</p>'

        ## Log in and render the New Media page.
        self._login()
        new_response = self.app.get(new_url, status=200)

        # Make a new media object by filling out the form.
        form = new_response.forms['media-form']
        form['title'] = title
        form['author_name'] = name
        form['author_email'] = email
        form['description'] = description
        form['notes'] = ''
        assert form.action == save_url
        save_response = form.submit()
        assert save_response.status_int == 302
        media_1 = fetch_row(Media, slug=slug)
        media_1_id = media_1.id
        edit_url = url(controller='admin/media', action='edit', id=media_1.id)
        assert save_response.location == 'http://localhost%s' % edit_url

        # Make a new media object by adding a new file
        files = [
            ('file', '/some/fake/filename.mp3', 'FILE CONTENT: This is not an MP3 file at all, but this random string will work for our purposes.')
        ]
        fields = {
            'url': '',
        }
        add_response = self.app.post(add_url, params=fields, upload_files=files)
        assert add_response.status_int == 200
        assert add_response.headers['Content-Type'] == 'application/json'
        add_json = simplejson.loads(add_response.body)
        assert add_json['success'] == True
        assert 'message' not in add_json
        media_2_id = add_json['media_id']
        file_2_id = add_json['file_id']

        # Assert that the stub file was named properly.
        file_2 = fetch_row(MediaFile, file_2_id)
        file_2_uri = [u for u in file_2.get_uris() if u.scheme == 'file'][0]
        file_2_basename = os.path.basename(file_2_uri.file_uri)
        assert file_2_basename.startswith('%d_%d_' % (media_2_id, file_2_id))
        assert file_2_basename.endswith('.mp3')

        # Merge the objects!
        merge_url = url(controller='admin/media', action='merge_stubs', orig_id=media_1_id, input_id=media_2_id)
        merge_response = self.app.get(merge_url)
        merge_json = simplejson.loads(merge_response.body)
        assert merge_json['success'] == True
        assert merge_json['media_id'] == media_1_id

        # Ensure that the correct objects were created/destroyed
        try:
            media_2 = fetch_row(Media, media_2_id)
            raise Exception('Stub media object not properly deleted!')
        except webob.exc.HTTPException, e:
            if e.code != 404:
                raise

        media_1 = fetch_row(Media, media_1_id)
        file_1 = media_1.files[0]

        # Ensure that the file was correctly renamed and has the right content.
        assert media_1.type == 'audio'
        assert file_1.type == 'audio'
        assert file_1.container == 'mp3'
        file_uri = [u for u in file_1.get_uris() if u.scheme == 'file'][0]
        file_path = file_uri.file_uri[len("file://"):]
        base_name = os.path.basename(file_path)
        expected_base_name = '%d_%d_%s.%s' % (media_1.id, file_1.id, media_1.slug, file_1.container)
        assert base_name == expected_base_name, "Got basename %s, but expected %s" % (base_name, expected_base_name)
        assert os.path.exists(file_path)
        file = open(file_path)
        content = file.read()
        file.close()
        assert content == files[0][2]
