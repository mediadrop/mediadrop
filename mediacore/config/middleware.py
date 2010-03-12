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

"""TurboGears middleware initialization"""
import os
from mediacore.config.app_cfg import base_config
from paste.deploy.converters import asbool
from tg import config
from mediacore.config.environment import load_environment

# Use base_config to setup the necessary WSGI App factory.
# make_base_app will wrap the TG2 app with all the middleware it needs.
make_base_app = base_config.setup_tg_wsgi_app(load_environment)

class FastCGIFixMiddleware(object):
    """Remove FastCGI script name from the SCRIPT_NAME

    mod_rewrite doesn't do a perfect job of hiding it's actions to the
    underlying script. This means that the name of the FastCGI script is
    prepended to the SCRIPT_NAME. This causes TurboGears routing to
    get confused.

    Here we remove the FastCGI script name before any processing is done
    and avoid any errors.
    """
    def __init__(self, app, global_conf=None):
        self.app = app

    def __call__(self, environ, start_response):
        real_path = config.get('fastcgi_real_path')
        rewrite_path = config.get('fastcgi_rewrite_path').rstrip(os.sep)
        environ['SCRIPT_NAME'] = \
            environ['SCRIPT_NAME'].replace(real_path, rewrite_path)
        return self.app(environ, start_response)


def make_app(global_conf, full_stack=True, **app_conf):
    app = make_base_app(global_conf, full_stack=True, **app_conf)
    # Wrap your base turbogears app with custom middleware
    if asbool(config.get('fastcgi', False)):
        app = FastCGIFixMiddleware(app)
    return app


