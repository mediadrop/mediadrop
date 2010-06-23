from mediacore.tests import *

test_user = 'admin'
test_password = 'admin'

class TestLoginController(TestController):

    def test_forced_login(self):
        """
        Anonymous users should be redirected to the login form when they
        request a protected area.
        """
        restricted_url = url(controller='admin', action='index')
        login_form_url = url(controller='login', action='login')
        post_login_url = url(controller='login', action='post_login')

        # Requesting a protected area as anonymous should redirect to the
        # login form page
        restricted_page = self.app.get(restricted_url, status=302)
        assert restricted_page.location.startswith(
                    'http://localhost%s' % login_form_url)

        # Follow the redirect to the login page and fill out the login form.
        login_page = restricted_page.follow(status=200)
        login_page.form['login'] = test_user
        login_page.form['password'] = test_password

        # Submitting the login form should redirect us to the 'post_login' page
        # TODO: Figure out why this post_login page is necessary, or at least why
        #       it's not mentioned in the repoze.who-testutil docs.
        login_handler_page = login_page.form.submit(status=302)
        assert login_handler_page.location.startswith(
                    'http://localhost%s' % post_login_url)

        # The post_login page should set up our authentication cookies
        # and redirect to the initially requested page.
        post_login_handler_page = login_handler_page.follow(status=302)
        assert post_login_handler_page.location == \
                'http://localhost%s' % restricted_url
        assert 'authtkt' in post_login_handler_page.request.cookies, \
               "Session cookie wasn't defined: %s" % post_login_handler_page.request.cookies

        # Follow the redirect to check that we were correctly authenticated:
        initial_page = post_login_handler_page.follow(status=200)
