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

"""Pylons middleware initialization"""
from beaker.middleware import SessionMiddleware
from paste.cascade import Cascade
from paste.registry import RegistryManager
from paste.urlparser import StaticURLParser
from paste.deploy.converters import asbool
from pylons.middleware import ErrorHandler, StatusCodeRedirect
from pylons.wsgiapp import PylonsApp
from routes.middleware import RoutesMiddleware

import os
import tw.api
from paste.deploy.converters import asbool
from mediacore.config.environment import load_environment
from mediacore.lib.auth import add_auth

class FastCGIFixMiddleware(object):
    """Remove FastCGI script name from the SCRIPT_NAME

    mod_rewrite doesn't do a perfect job of hiding it's actions to the
    underlying script. This means that the name of the FastCGI script is
    prepended to the SCRIPT_NAME. This causes TurboGears routing to
    get confused.

    Here we remove the FastCGI script name before any processing is done
    and avoid any errors.
    """
    def __init__(self, app, config, global_conf=None):
        self.app = app
        self.config = config

    def __call__(self, environ, start_response):
        real_path = self.config.get('fastcgi_real_path')
        rewrite_path = self.config.get('fastcgi_rewrite_path').rstrip(os.sep)
        environ['SCRIPT_NAME'] = \
            environ['SCRIPT_NAME'].replace(real_path, rewrite_path)
        return self.app(environ, start_response)

def make_app(global_conf, full_stack=True, static_files=True, **app_conf):
    """Create a Pylons WSGI application and return it

    ``global_conf``
        The inherited configuration for this application. Normally from
        the [DEFAULT] section of the Paste ini file.

    ``full_stack``
        Whether this application provides a full WSGI stack (by default,
        meaning it handles its own exceptions and errors). Disable
        full_stack when this application is "managed" by another WSGI
        middleware.

    ``static_files``
        Whether this application serves its own static files; disable
        when another web server is responsible for serving them.

    ``app_conf``
        The application's local configuration. Normally specified in
        the [app:<name>] section of the Paste ini file (where <name>
        defaults to main).

    """
    # Configure the Pylons environment
    config = load_environment(global_conf, app_conf)

    # The Pylons WSGI app
    app = PylonsApp(config=config)

    # Routing/Session/Cache Middleware
    app = RoutesMiddleware(app, config['routes.map'], singleton=False)
    app = SessionMiddleware(app, config)

    # CUSTOM MIDDLEWARE HERE (filtered by error handling middlewares)

    # Set up repoze.what-quickstart authentication:
    # http://wiki.pylonshq.com/display/pylonscookbook/Authorization+with+repoze.what
    app = add_auth(app, config)

    # Set up the FastCGI wrapper, if requested.
    if asbool(config.get('fastcgi', False)):
        app = FastCGIFixMiddleware(app, config)

    # Set up the TW middleware, as per errors and instructions at:
    # http://groups.google.com/group/toscawidgets-discuss/browse_thread/thread/c06950b8d1f62db9
    # http://toscawidgets.org/documentation/ToscaWidgets/install/pylons_app.html
    app = tw.api.make_middleware(app, {
        'toscawidgets.framework': 'pylons',
        'toscawidgets.framework.default_view': 'genshi',
    })

    # END CUSTOM MIDDLEWARE

    if asbool(full_stack):
        # Handle Python exceptions
        app = ErrorHandler(app, global_conf, **config['pylons.errorware'])

        # Display error documents for 401, 403, 404 status codes (and
        # 500 when debug is disabled)
        if asbool(config['debug']):
            app = StatusCodeRedirect(app)
        else:
            app = StatusCodeRedirect(app, [400, 401, 403, 404, 500])

    # Establish the Registry for this application
    app = RegistryManager(app)

    if asbool(static_files):
        # Serve static files
        static_app = StaticURLParser(config['pylons.paths']['static_files'])
        app = Cascade([static_app, app])

    app.config = config
    return app

