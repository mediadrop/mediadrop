# This file is a part of MediaCore CE, Copyright 2009-2012 MediaCore Inc.
# The source code contained in this file is licensed under the GPL.
# See LICENSE.txt in the main project directory, for more information.
"""
Auth-related helpers

Provides a custom request classifier for repoze.who to allow for Flash uploads.
"""

import re

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


class MediaCoreAuthenticatorPlugin(SQLAlchemyAuthenticatorPlugin):
    def authenticate(self, environ, identity):
        login = super(MediaCoreAuthenticatorPlugin, self).authenticate(environ, identity)
        if login is None:
            return None
        user = self.get_user(login)
        # The return value of this method is used to identify the user later on.
        # As the username can be changed, that's not really secure and may 
        # lead to confusion (users is logged out unexpectedly, best case) or 
        # account take-over (impersonation, worst case).
        # The user ID is considered constant and likely the best choice here.
        return user.user_id


class MediaCoreCookiePlugin(AuthTktCookiePlugin):
    def __init__(self, secret, **kwargs):
        if kwargs.get('userid_checker') is not None:
            raise TypeError("__init__() got an unexpected keyword argument 'userid_checker'")
        kwargs['userid_checker'] = self._check_userid
        super(MediaCoreCookiePlugin, self).__init__(secret, **kwargs)
    
    def _check_userid(self, user_id):
        # only accept numeric user_ids. In MediaCore < 1.0 the cookie contained
        # the user name, so invalidate all these old sessions.
        if re.search('[^0-9]', user_id):
            return False
        return True

def who_config(config):
    auth_by_username = MediaCoreAuthenticatorPlugin(User, DBSession)
    
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
    seconds_30_days = 30*24*60*60 # session expires after 30 days
    cookie = MediaCoreCookiePlugin(cookie_secret, 
        cookie_name='authtkt', 
        timeout=seconds_30_days, # session expires after 30 days
        reissue_time=seconds_30_days/2, # reissue cookie after 15 days
    )

    sql_user_md = SQLAlchemyUserMDPlugin(User, DBSession)
    sql_user_md.translations['user_name'] = 'user_id'

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
    groups_adapter = SqlGroupsAdapter(Group, User, DBSession)
    groups_adapter.translations['item_name'] = 'user_id'
    permission_adapter = SqlPermissionsAdapter(Permission, Group, DBSession)
    return setup_auth(app, {'sql_groups': groups_adapter}, 
        {'sql_permissions': permission_adapter}, **who_config(config))


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
