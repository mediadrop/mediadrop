# This file is a part of MediaCore CE, Copyright 2009-2012 MediaCore Inc.
# The source code contained in this file is licensed under the GPL.
# See LICENSE.txt in the main project directory, for more information.

# FIXME: This is a big one: We actually need to implement auth still, with the new pylons framework.

from pylons import request, response, session, tmpl_context
from pylons.controllers.util import abort, redirect

from mediacore.lib.base import BaseController
from mediacore.lib.helpers import redirect, url_for
from mediacore.lib.decorators import expose, expose_xhr, observable, validate, paginate
from mediacore.model import fetch_row, Podcast, Media, Category
from mediacore.plugin import events

import logging
log = logging.getLogger(__name__)

class LoginController(BaseController):
    @expose('login.html')
    @observable(events.LoginController.login)
    def login(self, came_from=None, **kwargs):
        login_counter = request.environ.get('repoze.who.logins', 0)
        if login_counter > 0:
            # TODO: display a 'wrong username/password' warning
            pass

        if not came_from:
            came_from = url_for(controller='admin', action='index', qualified=True)

        return dict(
            login_counter = str(login_counter),
            came_from = came_from,
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
        if request.identity:
            userid = request.identity['repoze.who.userid']
        else:
            login_counter = request.environ['repoze.who.logins'] + 1

        if came_from:
            redirect(came_from)
        else:
            redirect(controller='admin', action='index')

    @expose()
    @observable(events.LoginController.post_logout)
    def post_logout(self, came_from=None, **kwargs):
        redirect('/')

    def __call__(self, environ, start_response):
        """Invoke the Controller"""
        # BaseController.__call__ dispatches to the Controller method
        # the request is routed to. This routing information is
        # available in environ['pylons.routes_dict']
        request.identity = request.environ.get('repoze.who.identity')
        tmpl_context.identity = request.identity
        return BaseController.__call__(self, environ, start_response)
