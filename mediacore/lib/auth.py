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

from repoze.who.classifiers import default_request_classifier
from paste.request import parse_formvars

def classifier_for_flash_uploads(environ):
    """Normally classifies the request as browser, dav or xmlpost.

    When the Flash uploader is sending a file, it appends the authtkt session ID
    to the POST data so we spoof the cookie header so that the auth code will
    think this was a normal request. In the process, we overwrite any
    pseudo-cookie data that is sent by Flash.

    TODO: Currently overwrites the HTTP_COOKIE, should ideally append.
    """
    classification = default_request_classifier(environ)
    if classification == 'browser' and environ['REQUEST_METHOD'] == 'POST'\
                                   and 'Flash' in environ['HTTP_USER_AGENT']:
        try:
            session_key = environ['repoze.who.plugins']['cookie'].cookie_name
            session_id = parse_formvars(environ)[session_key]
            environ['HTTP_COOKIE'] = '%s=%s' % (session_key, session_id)
            del environ['paste.cookies']
            del environ['paste.cookies.dict']
        except (KeyError, AttributeError):
            pass
    return classification
