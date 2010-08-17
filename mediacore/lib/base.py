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
The Base Controller API

Provides controller classes for subclassing.
"""
import os
import time
import urllib2

from paste.deploy.converters import asbool
from pylons import app_globals, config, request, response, tmpl_context
from pylons.controllers import WSGIController
from pylons.controllers.util import abort
from repoze.what.plugins.pylonshq import ControllerProtector
from repoze.what.predicates import Predicate

from mediacore.lib import helpers
from mediacore.model.meta import DBSession

__all__ = ['BareBonesController', 'BaseController']

class BareBonesController(WSGIController):
    """
    The Bare Bones extension of a WSGIController needed for this app to function
    """
    def __init__(self, *args, **kwargs):
        """Implements TG2 style controller-level permissions requirements.

        If the allow_only class attribute has been set, wrap the __before__
        method with an ActionProtector using the predicate defined there.
        """
        if hasattr(self, 'allow_only') \
        and isinstance(self.allow_only, Predicate):
            # ControllerProtector wraps the __before__ method of this instance.
            cp = ControllerProtector(self.allow_only)
            self = cp(self)
        WSGIController.__init__(self, *args, **kwargs)

    def _get_method_args(self):
        """Retrieve the method arguments to use with inspect call.

        By default, this uses Routes to retrieve the arguments,
        override this method to customize the arguments your controller
        actions are called with.

        For MediaCore, we extend this to include all GET and POST params.

        NOTE: If the action does not define \*\*kwargs, then only the kwargs
              that it defines will be passed to it when it is called.
        """
        kwargs = request.params.mixed()
        kwargs.update(WSGIController._get_method_args(self))
        return kwargs

    def __before__(self, *args, **kwargs):
        """This method is called before your action is.
        It should be used for setting up variables/objects, restricting access
        to other actions, or other tasks which should be executed before the
        action is called.

        NOTE: if this method is wrapped in an ActionProtector, all methods of
        the class will be protected it. See the __init__ method.
        """
        action = getattr(self, kwargs['action'])
        # The expose decorator sets the exposed attribute on controller
        # actions. If a method is not exposed, do not allow access to it.
        if not getattr(action, 'exposed', False):
            abort(status_code=404)

class BaseController(BareBonesController):
    """
    The BaseController for all our controllers.

    Adds functionality for fetching and updating an externally generated
    template.
    """
    def __init__(self, *args, **kwargs):
        """Initialize the controller and hook in the external template, if any.

        These settings used are pulled from your INI config file:

            external_template
                Flag to enable or disable use of the external template
            external_template_name
                The name to load/save the external template as
            external_template_url
                The URL to pull the external template from
            external_template_timeout
                The number of seconds before the template should be refreshed

        See also :meth:`update_external_template` for more information.
        """
        tmpl_context.layout_template = config['layout_template']
        tmpl_context.external_template = None

        # FIXME: This external template is only ever updated on server startup
        if asbool(config['external_template']):
            tmpl_name = config['external_template_name']
            tmpl_url = config['external_template_url']
            timeout = config['external_template_timeout']
            tmpl_context.external_template = tmpl_name

            try:
                self.update_external_template(tmpl_url, tmpl_name, timeout)
            except:
                # Catch the error because the external template is noncritical.
                # TODO: Add error reporting here.
                pass

        BareBonesController.__init__(self, *args, **kwargs)

    def __call__(self, environ, start_response):
        """Commit or rollback the DBSession for every request.

        Your controller may override this method and have it call
        :meth:`BareBonesController.__call__` directly to avoid
        this transaction management.

        """
        try:
            app_iter = BareBonesController.__call__(self, environ,
                                                    start_response)
        except:
            # An unexpected error has occurred that the WebError will catch
            DBSession.rollback()
            raise
        else:
            # webob.exc.HTTPException's are caught and turned into a regular
            # responses in WSGIController._inspect_call. Veto error responses:
            if 200 <= response.status_int < 400:
                DBSession.commit()
            else:
                DBSession.rollback()
            return app_iter

    def update_external_template(self, tmpl_url, tmpl_name, timeout):
        """Conditionally fetch and cache the remote template.

        This method will only work on \*nix systems.

        :param tmpl_url: The URL to fetch the Genshi template from.
        :param tmpl_name: The template name to save under.
        :param timeout: Number of seconds to wait before refreshing
        :rtype: bool
        :returns: ``True`` if updated successfully, ``False`` if unnecessary.
        :raises Exception: If update fails unexpectedly due to IO problems.

        """
        current_dir = os.path.dirname(__file__)
        tmpl_path = '%s/../templates/%s.html' % (current_dir, tmpl_name)
        tmpl_tmp_path = '%s/../templates/%s_new.html' % (current_dir, tmpl_name)

        # Stat the main template file.
        try:
            statinfo = os.stat(tmpl_path)[:10]
            st_mode, st_ino, st_dev, st_nlink,\
                st_uid, st_gid, st_size, st_ntime,\
                st_mtime, st_ctime = statinfo

            # st_mtime and now are both unix timestamps.
            now = time.time()
            diff = now - st_mtime

            # if the template file is less than 5 minutes old, return
            if diff < float(timeout):
                return False
        except OSError, e:
            # Continue if the external template hasn't ever been created yet.
            if e.errno != 2:
                raise e

        try:
            # If the tmpl_tmp_path file exists
            # That means that another instance of mediacore is writing to it
            # Return immediately
            os.stat(tmpl_tmp_path)
            return False
        except OSError, e:
            # If the stat call failed, create the file. and continue.
            tmpl_tmp_file = open(tmpl_tmp_path, 'w')

        # Download the template, replace windows style newlines
        tmpl_contents = urllib2.urlopen(tmpl_url)
        s = tmpl_contents.read().replace("\r\n", "\n")
        tmpl_contents.close()

        # Write to the temp template file.
        tmpl_tmp_file.write(s)
        tmpl_tmp_file.close()

        # Rename the temp file to the main template file
        # NOTE: This only works on *nix, and is only guaranteed to work if the
        #       files are on the same filesystem.
        #       see http://docs.python.org/library/os.html#os.rename
        os.rename(tmpl_tmp_path, tmpl_path)
