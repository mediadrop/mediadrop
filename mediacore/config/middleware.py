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
from genshi.template import loader
from genshi.template.plugin import MarkupTemplateEnginePlugin
from paste.cascade import Cascade
from paste.gzipper import make_gzip_middleware
from paste.registry import RegistryManager
from paste.urlmap import URLMap
from paste.urlparser import StaticURLParser
from paste.deploy.converters import asbool
from paste.deploy.config import PrefixMiddleware
from pylons.i18n.translation import lazy_ugettext, ugettext
from pylons.middleware import ErrorHandler, StatusCodeRedirect
from pylons.wsgiapp import PylonsApp
from routes.middleware import RoutesMiddleware
from tw.core.view import EngineManager
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

class FastCGIScriptStripperMiddleware(object):
    """Strip the given fcgi_script_name from the end of environ['SCRIPT_NAME'].

    Useful for the default FastCGI deployment, where mod_rewrite is used to
    avoid having to put the .fcgi file name into the URL.
    """
    def __init__(self, app, fcgi_script_name='/mediacore.fcgi'):
        self.app = app
        self.fcgi_script_name = fcgi_script_name
        self.cut = len(fcgi_script_name)

    def __call__(self, environ, start_response):
        script_name = environ.get('SCRIPT_NAME', '')
        if script_name.endswith(self.fcgi_script_name):
            environ['SCRIPT_NAME'] = script_name[:-self.cut]
        return self.app(environ, start_response)

def setup_tw_middleware(app, config):
    # Set up the TW middleware, as per errors and instructions at:
    # http://groups.google.com/group/toscawidgets-discuss/browse_thread/thread/c06950b8d1f62db9
    # http://toscawidgets.org/documentation/ToscaWidgets/install/pylons_app.html
    def enable_i18n_for_template(template):
        template.filters.insert(0, Translator(ugettext))

    def filename_suffix_adder(inner_loader, suffix):
        def _add_suffix(filename):
            return inner_loader(filename + suffix)
        return _add_suffix

    # Ensure that the toscawidgets template loader includes the search paths
    # from our main template loader.
    tw_engine_options = {'genshi.loader_callback': enable_i18n_for_template}
    tw_engines = EngineManager(extra_vars_func=None, options=tw_engine_options)
    tw_engines['genshi'] = MarkupTemplateEnginePlugin()
    tw_engines['genshi'].loader = config['pylons.app_globals'].genshi_loader

    # Disable the built-in package name template resolution.
    tw_engines['genshi'].use_package_naming = False

    # Rebuild package name template resolution using mostly standard Genshi
    # load functions. With our customizations to the TemplateLoader, the
    # absolute paths that the builtin resolution produces are erroneously
    # treated as being relative to the search path.

    # Search the tw templates dir using the pkg_resources API.
    # Expected input: 'input_field.html'
    tw_loader = loader.package('tw.forms', 'templates')

    # Include the .html extension automatically.
    # Expected input: 'input_field'
    tw_loader = filename_suffix_adder(tw_loader, '.html')

    # Apply this loader only when the filename starts with tw.forms.templates.
    # This prefix is stripped off when calling the above loader.
    # Expected input: 'tw.forms.templates.input_field'
    tw_loader = loader.prefixed(**{'tw.forms.templates.': tw_loader})

    # Add this path to our global loader
    tw_engines['genshi'].loader.search_path.append(tw_loader)

    app = tw.api.make_middleware(app, {
        'toscawidgets.framework': 'pylons',
        'toscawidgets.framework.default_view': 'genshi',
        'toscawidgets.framework.translator': lazy_ugettext,
        'toscawidgets.framework.engines': tw_engines,
    })
    return app

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

    # ToscaWidgets Middleware
    app = setup_tw_middleware(app, config)

    # Strip the name of the .fcgi script, if using one, from the SCRIPT_NAME
    app = FastCGIScriptStripperMiddleware(app)

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
        # Serve static files from our public directory
        public_app = StaticURLParser(config['pylons.paths']['static_files'])

        static_urlmap = URLMap()
        # Serve static files from all plugins
        for dir, path in plugin_mgr.public_paths().iteritems():
            static_urlmap[dir] = StaticURLParser(path)

        # Serve static media and podcast images from outside our public directory
        for image_type in ('media', 'podcasts'):
            dir = '/images/' + image_type
            path = os.path.join(config['image_dir'], image_type)
            static_urlmap[dir] = StaticURLParser(path)

        # Check for the closure-library in the default location.
        # We want to serve goog closure code for debugging uncompiled js.
        if config['debug']:
            goog_path = os.path.join(config['pylons.paths']['root'], '..',
                'closure-library', 'closure', 'goog')
            if os.path.exists(goog_path):
                static_urlmap['/scripts/goog'] = StaticURLParser(goog_path)

        app = Cascade([public_app, static_urlmap, app])

    if asbool(config.get('enable_gzip', 'true')):
        app = make_gzip_middleware(app, global_conf)

    app.config = config
    return app
