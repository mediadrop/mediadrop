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
import os

from beaker.middleware import SessionMiddleware
from genshi.filters.i18n import Translator
from paste.cascade import Cascade
from paste.registry import RegistryManager
from paste.urlparser import StaticURLParser
from paste.deploy.converters import asbool
from paste.deploy.config import PrefixMiddleware
from pylons.i18n.translation import lazy_ugettext, ugettext
from pylons.middleware import ErrorHandler, StatusCodeRedirect
from pylons.wsgiapp import PylonsApp
from routes.middleware import RoutesMiddleware
import tw.api

from mediacore.config.environment import load_environment
from mediacore.lib.auth import add_auth
from mediacore.model.meta import DBSession

def setup_prefix_middleware(app, global_conf, proxy_prefix):
    """Add prefix middleware.

    Essentially replaces request.environ[SCRIPT_NAME] with the prefix defined
    in the .ini file.

    See: http://wiki.pylonshq.com/display/pylonsdocs/Configuration+Files#prefixmiddleware
    """
    app = PrefixMiddleware(app, global_conf, proxy_prefix)
    return app

class DBSessionRemoverMiddleware(object):
    """Ensure the contextual session ends at the end of the request."""
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        try:
            return self.app(environ, start_response)
        finally:
            DBSession.remove()

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
    plugin_mgr = config['pylons.app_globals'].plugin_mgr

    # The Pylons WSGI app
    app = PylonsApp(config=config)

    # Allow the plugin manager to tweak our WSGI app
    app = plugin_mgr.wrap_pylons_app(app)

    # Routing/Session/Cache Middleware
    app = RoutesMiddleware(app, config['routes.map'], singleton=False)
    app = SessionMiddleware(app, config)

    # CUSTOM MIDDLEWARE HERE (filtered by error handling middlewares)

    # Set up repoze.what-quickstart authentication:
    # http://wiki.pylonshq.com/display/pylonscookbook/Authorization+with+repoze.what
    app = add_auth(app, config)

    # Set up the TW middleware, as per errors and instructions at:
    # http://groups.google.com/group/toscawidgets-discuss/browse_thread/thread/c06950b8d1f62db9
    # http://toscawidgets.org/documentation/ToscaWidgets/install/pylons_app.html
    def enable_i18n_for_template(template):
        template.filters.insert(0, Translator(ugettext))

    # Ensure that the toscawidgets template loader includes the search paths
    # from our main template loader.
    from tw.core.view import EngineManager
    from genshi.template.plugin import MarkupTemplateEnginePlugin
    tw_engine_options = {'genshi.loader_callback': enable_i18n_for_template}
    tw_engines = EngineManager(extra_vars_func=None, options=tw_engine_options)
    tw_engines['genshi'] = MarkupTemplateEnginePlugin()
    tw_engines['genshi'].loader = config['pylons.app_globals'].genshi_loader

    app = tw.api.make_middleware(app, {
        'toscawidgets.framework': 'pylons',
        'toscawidgets.framework.default_view': 'genshi',
        'toscawidgets.framework.translator': lazy_ugettext,
        'toscawidgets.framework.engines': tw_engines,
    })

    # If enabled, set up the proxy prefix for routing behind
    # fastcgi and mod_proxy based deployments.
    if config.get('proxy_prefix', None):
        app = setup_prefix_middleware(app, global_conf, config['proxy_prefix'])

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

    # Cleanup the DBSession only after errors are handled
    app = DBSessionRemoverMiddleware(app)

    # Establish the Registry for this application
    app = RegistryManager(app)

    if asbool(static_files):
        # Serve static files
        static_app = StaticURLParser(config['pylons.paths']['static_files'])
        app = Cascade([static_app] + plugin_mgr.static_url_apps() + [app])

    app.config = config
    return app
