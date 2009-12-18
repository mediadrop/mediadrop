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

Provides the BaseController class for subclassing and other utils useful
when working with controllers.

"""
import os
import time
import urllib2
import functools

import routes
from tg import config, request, response, tmpl_context, exceptions, expose
from tg.controllers import RoutingController
from paste.deploy.converters import asbool

# Import for convenience in controllers
from tg import validate, flash
from mediacore.model.settings import fetch_setting
from mediacore.lib.paginate import paginate


class BaseController(RoutingController):
    """
    The BaseController for all our controllers.

    If you want to revert to TG-style object dispatch, have this class
    inherit from :class:`tg.controllers.TGController`.

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
        # First, define the email that topic suggestions should be sent to.
        support_emails = fetch_setting('email_support_requests')
        support_emails = support_emails.split(',') if support_emails else ['']
        tmpl_context.suggest_topic_email = support_emails[0]

        tmpl_context.layout_template = config.layout_template
        tmpl_context.external_template = None

        if asbool(config.external_template):
            tmpl_name = config.external_template_name
            tmpl_url = config.external_template_url
            timeout = config.external_template_timeout
            tmpl_context.external_template = tmpl_name

            try:
                self.update_external_template(tmpl_url, tmpl_name, timeout)
            except:
                # Catch the error because the external template is noncritical.
                # TODO: Add error reporting here.
                pass

        super(BaseController, self).__init__(self, *args, **kwargs)

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


def url_for(*args, **kwargs):
    """Compose a URL using the route mappings in :mod:`mediacore.config.routes`.

    This is a wrapper for :func:`routes.util.url_for`, all arguments are passed.

    Using the REPLACE and REPLACE_WITH GET variables, if set,
    this method replaces the first instance of REPLACE in the
    url string. This can be used to proxy an action at a different
    URL.

    For example, by using an apache mod_rewrite rule:

    .. sourcecode:: apacheconf

        RewriteRule ^/proxy_url(/.\*){0,1}$ /proxy_url$1?_REP=/mycont/actionA&_RWITH=/proxyA [qsappend]
        RewriteRule ^/proxy_url(/.\*){0,1}$ /proxy_url$1?_REP=/mycont/actionB&_RWITH=/proxyB [qsappend]
        RewriteRule ^/proxy_url(/.\*){0,1}$ /mycont/actionA$1 [proxy]

    """
    # Convert unicode to str utf-8 for routes
    if args:
        args = [(val.encode('utf-8') if isinstance(val, basestring) else val)
                for val in args]
    if kwargs:
        kwargs = dict(
            (key, val.encode('utf-8') if isinstance(val, unicode) else val)\
            for key, val in kwargs.items()
        )

    url = routes.url_for(*args, **kwargs)

    # Make the replacements
    repl = request.str_GET.getall('_REP')
    repl_with = request.str_GET.getall('_RWITH')
    for i in range(0, min(len(repl), len(repl_with))):
        url = url.replace(repl[i], repl_with[i], 1)

    return url

def redirect(*args, **kwargs):
    """Compose a URL using :func:`url_for` and raise a redirect.

    :raises: :class:`tg.exceptions.HTTPFound`
    """
    url = url_for(*args, **kwargs)
    found = exceptions.HTTPFound(location=url)
    raise found.exception

class expose_xhr(object):
    """
    Expose different templates for normal vs XMLHttpRequest requests.

    Example::

        class MyController(BaseController):
            @expose_xhr('mediacore.templates.list',
                        'mediacore.templates.list_partial')
            def

    """
    def __init__(self, template_norm='', template_xhr='json', **kwargs):
        self.normal_decorator = expose(template=template_norm, **kwargs)
        self.xhr_decorator = expose(template=template_xhr, **kwargs)

    def __call__(self, func):
        # create a wrapper function to override the template,
        # in the case that this is an xhr request
        @functools.wraps(func)
        def f(*args, **kwargs):
            if request.is_xhr:
               return self.xhr_decorator.__call__(func)(*args, **kwargs)
            else:
               return self.normal_decorator.__call__(func)(*args, **kwargs)

        # set up the normal decorator so that we have the correct
        # __dict__ properties to copy over. namely 'decoration'
        func = self.normal_decorator.__call__(func)

        # copy over all the special properties added to func
        for i in func.__dict__:
            f.__dict__[i] = func.__dict__[i]

        return f
