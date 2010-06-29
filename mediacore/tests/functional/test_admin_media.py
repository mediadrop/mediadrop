from mediacore.tests import *
from mediacore.model import DBSession, Media, fetch_row

class TestMediaController(TestController):

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
        slug = 'add-new-media-test' # this should be unique
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
