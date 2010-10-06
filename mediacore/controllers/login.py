# This file is a part of MediaCore, Copyright 2009 Simple Station Inc.
#
# MediaCore is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# MediaCore is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

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
    def login(self, came_from=url_for(controller='admin', action='index'), **kwargs):
        login_counter = request.environ.get('repoze.who.logins', 0)
        if login_counter > 0:
            # TODO: display a 'wrong username/password' warning
            pass

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
    def post_login(self, came_from=url_for(controller='admin', action='index'), **kwargs):
        if not request.identity:
            login_counter = request.environ['repoze.who.logins'] + 1
            redirect(came_from)

        userid = request.identity['repoze.who.userid']
        redirect(came_from)

    @expose()
    @observable(events.LoginController.post_logout)
    def post_logout(self, came_from=None, **kwargs):
        redirect(url_for('/'))

    def __call__(self, environ, start_response):
        """Invoke the Controller"""
        # TGController.__call__ dispatches to the Controller method
        # the request is routed to. This routing information is
        # available in environ['pylons.routes_dict']
        request.identity = request.environ.get('repoze.who.identity')
        tmpl_context.identity = request.identity
        return BaseController.__call__(self, environ, start_response)
