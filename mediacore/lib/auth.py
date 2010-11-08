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

"""
Auth-related helpers

Provides a custom request classifier for repoze.who to allow for Flash uploads.
"""

from paste.request import parse_formvars
from repoze.what.plugins.quickstart import setup_sql_auth
from repoze.who.classifiers import default_request_classifier

from mediacore.config.routing import login_form_url, login_handler_url, logout_handler_url, post_login_url, post_logout_url
from mediacore.model.meta import DBSession
from mediacore.model import Group, Permission, User

__all__ = ['add_auth', 'classifier_for_flash_uploads']

def add_auth(app, config):
    """Add authentication and authorization middleware to the ``app``."""
    return setup_sql_auth(
        app, User, Group, Permission, DBSession,

        login_url = login_form_url,
        # XXX: These two URLs are intercepted by the sql_auth middleware
        login_handler = login_handler_url,
        logout_handler = logout_handler_url,

        # You may optionally define a page where you want users to be
        # redirected to on login:
        post_login_url = post_login_url,

        # You may optionally define a page where you want users to be
        # redirected to on logout:
        post_logout_url = post_logout_url,

        # Hook into the auth process to read the session ID out of the POST
        # vars during flash upload requests.
        classifier = classifier_for_flash_uploads,

        # override this if you would like to provide a different who plugin for
        # managing login and logout of your application
        form_plugin = None,

        # The salt used to encrypt auth cookie data. This value must be unique
        # to each deployment so it comes from the INI config file and is
        # randomly generated when you run paster make-config
        cookie_secret = config['sa_auth.cookie_secret']
    )


def classifier_for_flash_uploads(environ):
    """Normally classifies the request as browser, dav or xmlpost.

    When the Flash uploader is sending a file, it appends the authtkt session
    ID to the POST data so we spoof the cookie header so that the auth code
    will think this was a normal request. In the process, we overwrite any
    pseudo-cookie data that is sent by Flash.

    TODO: Currently overwrites the HTTP_COOKIE, should ideally append.
    """
    classification = default_request_classifier(environ)
    if classification == 'browser' \
    and environ['REQUEST_METHOD'] == 'POST' \
    and 'Flash' in environ.get('HTTP_USER_AGENT', ''):
        try:
            session_key = environ['repoze.who.plugins']['cookie'].cookie_name
            session_id = parse_formvars(environ)[session_key]
            environ['HTTP_COOKIE'] = '%s=%s' % (session_key, session_id)
            del environ['paste.cookies']
            del environ['paste.cookies.dict']
        except (KeyError, AttributeError):
            pass
    return classification
