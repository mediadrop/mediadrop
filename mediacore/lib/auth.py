# This file is a part of MediaCore CE, Copyright 2009-2012 MediaCore Inc.
# The source code contained in this file is licensed under the GPL.
# See LICENSE.txt in the main project directory, for more information.
"""
Auth-related helpers

Provides a custom request classifier for repoze.who to allow for Flash uploads.
"""

from repoze.what.middleware import setup_auth
from repoze.what.plugins.sql.adapters import (SqlGroupsAdapter, 
    SqlPermissionsAdapter)
from repoze.who.classifiers import (default_request_classifier, 
    default_challenge_decider)
from repoze.who.plugins.auth_tkt import AuthTktCookiePlugin
from repoze.who.plugins.friendlyform import FriendlyFormPlugin
from repoze.who.plugins.sa import (SQLAlchemyAuthenticatorPlugin, 
    SQLAlchemyUserMDPlugin)
from webob.request import Request

from mediacore.config.routing import (login_form_url, login_handler_url, 
    logout_handler_url, post_login_url, post_logout_url)
from mediacore.model.meta import DBSession
from mediacore.model import Group, Permission, User

__all__ = ['add_auth', 'classifier_for_flash_uploads']


def who_config(config):
    auth_by_username = SQLAlchemyAuthenticatorPlugin(User, DBSession)

    form = FriendlyFormPlugin(
        login_form_url,
        login_handler_url,
        post_login_url,
        logout_handler_url,
        post_logout_url,
        rememberer_name='cookie',
        charset='iso-8859-1',
    )
    cookie_secret = config['sa_auth.cookie_secret']
    cookie = AuthTktCookiePlugin(cookie_secret, cookie_name='authtkt')

    sql_user_md = SQLAlchemyUserMDPlugin(User, DBSession)

    who_args = {
        'authenticators': [
            ('auth_by_username', auth_by_username)
        ],
        'challenge_decider': default_challenge_decider,
        'challengers': [('form', form)],
        'classifier': classifier_for_flash_uploads,
        'identifiers': [('main_identifier', form), ('cookie', cookie)],
        'mdproviders': [('sql_user_md', sql_user_md)],
    }
    return who_args


def add_auth(app, config):
    """Add authentication and authorization middleware to the ``app``."""
    groups_adapters = {'sql_auth': SqlGroupsAdapter(Group, User, DBSession)}
    permission_adapters = {'sql_auth': SqlPermissionsAdapter(Permission, Group, DBSession)}
    return setup_auth(app, groups_adapters, permission_adapters, **who_config(config))


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
        session_key = environ['repoze.who.plugins']['cookie'].cookie_name
        # Construct a temporary request object since this is called before
        # pylons.request is populated. Re-instantiation later comes cheap.
        request = Request(environ)
        try:
            session_id = request.str_POST[session_key]
            environ['HTTP_COOKIE'] = '%s=%s' % (session_key, session_id)
        except KeyError:
            pass
    return classification
