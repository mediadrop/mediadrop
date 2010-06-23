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

    def test_voluntary_login_and_logout(self):
        """
        Voluntary logins should redirect to the main admin page on
        success. Logout should redirect to the main / page.
        """
        admin_url = url(controller='admin', action='index')
        login_form_url = url(controller='login', action='login')
        post_login_url = url(controller='login', action='post_login')
        logout_handler_url = url(controller='login', action='logout_handler')
        post_logout_url = url(controller='login', action='post_logout')
        home_url = url('/')

        # Request, and fill out, the login form.
        login_page = self.app.get(login_form_url, status=200)
        login_page.form['login'] = test_user
        login_page.form['password'] = test_password

        # Submitting the login form should redirect us to the 'post_login' page
        login_handler_page = login_page.form.submit(status=302)
        assert login_handler_page.location.startswith(
                    'http://localhost%s' % post_login_url)

        # The post_login page should set up our authentication cookies
        # and redirect to the initially requested page.
        post_login_handler_page = login_handler_page.follow(status=302)
        assert post_login_handler_page.location == \
                'http://localhost%s' % admin_url
        assert 'authtkt' in post_login_handler_page.request.cookies, \
               "Session cookie wasn't defined: %s" % post_login_handler_page.request.cookies

        # Follow the redirect to check that we were correctly authenticated:
        admin_page = post_login_handler_page.follow(status=200)

        # Now 'click' the logout link.
        # This sends all relevant cookies, and ensures that the logout link is
        # actually displayed on the admin page.
        logout_handler_page = admin_page.click(linkid='logout', href=logout_handler_url)
        assert logout_handler_page.location.startswith(
                'http://localhost%s' % post_logout_url)

        # Follow the first logout redirect.
        # This should invalidate our authtkt cookie.
        post_logout_page = logout_handler_page.follow(status=302)
        assert post_logout_page.location == \
                'http://localhost%s' % home_url
        assert post_logout_page.request.cookies['authtkt'] == 'INVALID'

        # Follow the final logout redirect, back to the home page.
        home_page = post_logout_page.follow(status=200)
