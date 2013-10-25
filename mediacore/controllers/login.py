# This file is a part of MediaDrop (http://www.mediadrop.net),
# Copyright 2009-2013 MediaDrop contributors
# For the exact contribution history, see the git revision log.
# The source code contained in this file is licensed under the GPLv3 or
# (at your option) any later version.
# See LICENSE.txt in the main project directory, for more information.

from formencode import Invalid
from pylons import request, tmpl_context

from mediacore.forms.login import LoginForm
from mediacore.lib.base import BaseController
from mediacore.lib.helpers import redirect, url_for
from mediacore.lib.i18n import _
from mediacore.lib.decorators import expose, observable
from mediacore.plugin import events

import logging
log = logging.getLogger(__name__)

login_form = LoginForm()

class LoginController(BaseController):
    @expose('login.html')
    @observable(events.LoginController.login)
    def login(self, came_from=None, **kwargs):
        if request.environ.get('repoze.who.identity'):
            redirect(came_from or '/')
        
        # the friendlyform plugin requires that these values are set in the
        # query string
        form_url = url_for('/login/submit', 
            came_from=(came_from or '').encode('utf-8'), 
            __logins=str(self._is_failed_login()))
        
        login_errors = None
        if self._is_failed_login():
            login_errors = Invalid('dummy', None, {}, error_dict={
                '_form': Invalid(_('Invalid username or password.'), None, {}),
                'login': Invalid('dummy', None, {}),
                'password': Invalid('dummy', None, {}),
            })
        return dict(
            login_form = login_form,
            form_action = form_url,
            form_values = kwargs,
            login_errors = login_errors,
        )

    @expose()
    def login_handler(self):
        """This is a dummy method.

        Without a dummy method, Routes will throw a NotImplemented exception.
        Calls that would route to this method are intercepted by
        repoze.who, as defined in mediacore.lib.auth
        """
        pass

    @expose()
    def logout_handler(self):
        """This is a dummy method.

        Without a dummy method, Routes will throw a NotImplemented exception.
        Calls that would route to this method are intercepted by
        repoze.who, as defined in mediacore.lib.auth
        """
        pass

    @expose()
    @observable(events.LoginController.post_login)
    def post_login(self, came_from=None, **kwargs):
        if not request.identity:
            # The FriendlyForm plugin will always issue a redirect to 
            # /login/continue (post login url) even for failed logins.
            # If 'came_from' is a protected page (i.e. /admin) we could just 
            # redirect there and the login form will be displayed again with
            # our login error message.
            # However if the user tried to login from the front page, this 
            # mechanism doesn't work so go to the login method directly here.
            self._increase_number_of_failed_logins()
            return self.login(came_from=came_from)
        if came_from:
            redirect(came_from)
        # It is important to return absolute URLs (if app mounted in subdirectory)
        if request.perm.contains_permission(u'edit') or request.perm.contains_permission(u'admin'):
            redirect(url_for('/admin', qualified=True))
        redirect(url_for('/', qualified=True))

    @expose()
    @observable(events.LoginController.post_logout)
    def post_logout(self, came_from=None, **kwargs):
        redirect('/')

    def _is_failed_login(self):
        # repoze.who.logins will always be an integer even if the HTTP login 
        # counter variable contained a non-digit string
        return (request.environ.get('repoze.who.logins', 0) > 0)
    
    def _increase_number_of_failed_logins(self):
        request.environ['repoze.who.logins'] += 1
    
    def __call__(self, environ, start_response):
        """Invoke the Controller"""
        # BaseController.__call__ dispatches to the Controller method
        # the request is routed to. This routing information is
        # available in environ['pylons.routes_dict']
        request.identity = request.environ.get('repoze.who.identity')
        tmpl_context.identity = request.identity
        return BaseController.__call__(self, environ, start_response)
