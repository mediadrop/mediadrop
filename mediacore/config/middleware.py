# This file is a part of MediaDrop (http://www.mediadrop.net),
# Copyright 2009-2013 MediaDrop contributors
# For the exact contribution history, see the git revision log.
# The source code contained in this file is licensed under the GPLv3 or
# (at your option) any later version.
# See LICENSE.txt in the main project directory, for more information.
"""Pylons middleware initialization"""

import logging
import os
import threading

from beaker.middleware import SessionMiddleware
from genshi.template import loader
from genshi.template.plugin import MarkupTemplateEnginePlugin
from paste import gzipper
from paste.cascade import Cascade
from paste.registry import RegistryManager
from paste.response import header_value, remove_header
from paste.urlmap import URLMap
from paste.urlparser import StaticURLParser
from paste.deploy.converters import asbool
from paste.deploy.config import PrefixMiddleware
from pylons.middleware import ErrorHandler, StatusCodeRedirect
from pylons.wsgiapp import PylonsApp as _PylonsApp
from routes.middleware import RoutesMiddleware
import sqlalchemy
from sqlalchemy.pool import Pool
from sqlalchemy.exc import DisconnectionError
from tw.core.view import EngineManager
import tw.api

from mediacore import monkeypatch_method
from mediacore.config.environment import load_environment
from mediacore.lib.auth import add_auth
from mediacore.migrations.util import MediaDropMigrator
from mediacore.model import DBSession
from mediacore.plugin import events

log = logging.getLogger(__name__)

class PylonsApp(_PylonsApp):
    """
    Subclass PylonsApp to set our settings on the request.

    The settings are cached in ``request.settings`` but it's best to
    check the cache once, then make them accessible as a simple dict for
    the remainder of the request, instead of hitting the cache repeatedly.

    """
    def register_globals(self, environ):
        _PylonsApp.register_globals(self, environ)
        request = environ['pylons.pylons'].request

        if environ['PATH_INFO'] == '/_test_vars':
            # This is a dummy request, probably used inside a test or to build
            # documentation, so we're not guaranteed to have a database
            # connection with which to get the settings.
            request.settings = {
                'intentionally_empty': 'see mediacore.config.middleware',
            }
        else:
            request.settings = self.globals.settings

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

def create_tw_engine_manager(app_globals):
    def filename_suffix_adder(inner_loader, suffix):
        def _add_suffix(filename):
            return inner_loader(filename + suffix)
        return _add_suffix

    # Ensure that the toscawidgets template loader includes the search paths
    # from our main template loader.
    tw_engines = EngineManager(extra_vars_func=None)
    tw_engines['genshi'] = MarkupTemplateEnginePlugin()
    tw_engines['genshi'].loader = app_globals.genshi_loader

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
    return tw_engines

def setup_tw_middleware(app, config):
    app_globals = config['pylons.app_globals']
    app = tw.api.make_middleware(app, {
        'toscawidgets.framework': 'pylons',
        'toscawidgets.framework.default_view': 'genshi',
        'toscawidgets.framework.engines': create_tw_engine_manager(app_globals),
    })
    return app

class DBSanityCheckingMiddleware(object):
    def __init__(self, app, check_for_leaked_connections=False, 
                 enable_pessimistic_disconnect_handling=False):
        self.app = app
        self._thread_local = threading.local()
        self.is_leak_check_enabled = check_for_leaked_connections
        self.is_alive_check_enabled = enable_pessimistic_disconnect_handling
        if self.is_leak_check_enabled or self.is_alive_check_enabled:
            sqlalchemy.event.listen(Pool, 'checkout', self.on_connection_checkout)
        if self.is_leak_check_enabled:
            sqlalchemy.event.listen(Pool, 'checkin', self.on_connection_checkin)
    
    def __call__(self, environ, start_response):
        try:
            return self.app(environ, start_response)
        finally:
            leaked_connections = len(self.connections)
            if leaked_connections > 0:
                msg = 'DB connection leakage detected: ' + \
                    '%d db connection(s) not returned to the pool' % leaked_connections
                log.error(msg)
                self.connections.clear()
    
    @property
    def connections(self):
        if not hasattr(self._thread_local, 'connections'):
            self._thread_local.connections = dict()
        return self._thread_local.connections
    
    def check_for_live_db_connection(self, dbapi_connection):
        # Try to check that the current DB connection is usable for DB queries
        # by issuing a trivial SQL query. It can happen because the user set
        # the 'sqlalchemy.pool_recycle' time too high or simply because the
        # MySQL server was restarted in the mean time.
        # Without this check a user would get an internal server error and the
        # connection would be reset by the DBSessionRemoverMiddleware at the
        # end of that request.
        # This functionality below will prevent the initial "internal server
        # error".
        #
        # This approach is controversial between DB experts. A good blog post
        # (with an even better discussion highlighting pros and cons) is
        # http://www.mysqlperformanceblog.com/2010/05/05/checking-for-a-live-database-connection-considered-harmful/
        #
        # In MediaDrop the check is only done once per request (skipped for
        # static files) so it should be relatively light on the DB server.
        # Also the check can be disabled using the setting
        # 'sqlalchemy.check_connection_before_request = false'.
        #
        # possible optimization: check each connection only once per minute or so,
        # store last check time in private attribute of connection object.
        
        # code stolen from SQLAlchemy's 'Pessimistic Disconnect Handling' docs
        cursor = dbapi_connection.cursor()
        try:
            cursor.execute('SELECT 1')
        except:
            msg = u'received broken db connection from pool, resetting db session. ' + \
                u'If you see this error regularly and you use MySQL please check ' + \
                u'your "sqlalchemy.pool_recycle" setting (usually it is too high).'
            log.warning(msg)
            # The pool will try to connect again up to three times before 
            # raising an exception itself.
            raise DisconnectionError()
        cursor.close()
    
    def on_connection_checkout(self, dbapi_connection, connection_record, connection_proxy):
        if self.is_alive_check_enabled:
            self.check_for_live_db_connection(dbapi_connection)
        if self.is_leak_check_enabled:
            self.connections[id(dbapi_connection)] = True
    
    def on_connection_checkin(self, dbapi_connection, connection_record):
        connection_id = id(dbapi_connection)
        # connections might be returned *after* this middleware called
        # 'self.connections.clear()', we should not break in that case...
        if connection_id in self.connections:
            del self.connections[connection_id]


def setup_db_sanity_checks(app, config):
    check_for_leaked_connections = asbool(config.get('db.check_for_leaked_connections', False))
    enable_pessimistic_disconnect_handling = asbool(config.get('db.enable_pessimistic_disconnect_handling', False))
    if (not check_for_leaked_connections) and (not enable_pessimistic_disconnect_handling):
        return app
    
    return DBSanityCheckingMiddleware(app, check_for_leaked_connections=check_for_leaked_connections,
                                      enable_pessimistic_disconnect_handling=enable_pessimistic_disconnect_handling)

def setup_gzip_middleware(app, global_conf):
    """Make paste.gzipper middleware with a monkeypatch to exempt SWFs.

    Gzipping .swf files (application/x-shockwave-flash) provides no
    extra compression and it also breaks Flowplayer 3.2.3, and
    potentially others.

    """
    @monkeypatch_method(gzipper.GzipResponse)
    def gzip_start_response(self, status, headers, exc_info=None):
        self.headers = headers
        ct = header_value(headers, 'content-type')
        ce = header_value(headers, 'content-encoding')
        self.compressible = False
        # This statement is the only change in this monkeypatch:
        if ct and (ct.startswith('text/') or ct.startswith('application/')) \
            and 'zip' not in ct and ct != 'application/x-shockwave-flash':
            self.compressible = True
        if ce:
            self.compressible = False
        if self.compressible:
            headers.append(('content-encoding', 'gzip'))
        remove_header(headers, 'content-length')
        self.headers = headers
        self.status = status
        return self.buffer.write
    return gzipper.make_gzip_middleware(app, global_conf)

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
    alembic_migrations = MediaDropMigrator.from_config(config, log=log)
    if alembic_migrations.is_db_scheme_current():
        events.Environment.database_ready()
    else:
        log.warn('Running with an outdated database scheme. Please upgrade your database.')
    plugin_mgr = config['pylons.app_globals'].plugin_mgr

    # The Pylons WSGI app
    app = PylonsApp(config=config)

    # Allow the plugin manager to tweak our WSGI app
    app = plugin_mgr.wrap_pylons_app(app)

    # Routing/Session/Cache Middleware
    app = RoutesMiddleware(app, config['routes.map'], singleton=False)
    app = SessionMiddleware(app, config)

    # CUSTOM MIDDLEWARE HERE (filtered by error handling middlewares)

    # add repoze.who middleware with our own authorization library
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

        # by default Apache uses  a global alias for "/error" in the httpd.conf
        # which means that users can not send error reports through MediaDrop's
        # error page (because that POSTs to /error/report).
        # To make things worse Apache (at least up to 2.4) has no "unalias"
        # functionality. So we work around the issue by using the "/errors"
        # prefix (extra "s" at the end)
        error_path = '/errors/document'
        # Display error documents for 401, 403, 404 status codes (and
        # 500 when debug is disabled)
        if asbool(config['debug']):
            app = StatusCodeRedirect(app, path=error_path)
        else:
            app = StatusCodeRedirect(app, errors=(400, 401, 403, 404, 500),
                                     path=error_path)

    # Cleanup the DBSession only after errors are handled
    app = DBSessionRemoverMiddleware(app)

    # Establish the Registry for this application
    app = RegistryManager(app)

    app = setup_db_sanity_checks(app, config)

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

        # Serve appearance directory outside of public as well
        dir = '/appearance'
        path = os.path.join(config['app_conf']['cache_dir'], 'appearance')
        static_urlmap[dir] = StaticURLParser(path)

        # We want to serve goog closure code for debugging uncompiled js.
        if config['debug']:
            goog_path = os.path.join(config['pylons.paths']['root'], '..',
                'closure-library', 'closure', 'goog')
            if os.path.exists(goog_path):
                static_urlmap['/scripts/goog'] = StaticURLParser(goog_path)

        app = Cascade([public_app, static_urlmap, app])

    if asbool(config.get('enable_gzip', 'true')):
        app = setup_gzip_middleware(app, global_conf)

    app.config = config
    return app
