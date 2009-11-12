"""
The Base Controller API

Provides the BaseController class for subclassing and other utils useful
when working with controllers.

"""
import os
import time
import urllib2

from tg import config, request, tmpl_context
from tg.controllers import RoutingController

from paste.deploy.converters import asbool


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
                The name to load/save the external template as.
            external_template_url
                The URL to pull the external template from
            external_template_timeout
                The number of seconds before the template should be refreshed

        See also :meth:`update_external_template` for more information.
        """
        tmpl_context.layout_template = config.layout_template
        tmpl_context.external_template = None

        if asbool(config.external_template):
            tmpl_name = config.external_template_name
            tmpl_url = config.external_template_url
            timeout = config.external_template_timeout
            tmpl_context.external_template = tmpl_name

            try:
                self.update_external_template(tmpl_context.external_template,
                                              tmpl_name, timeout)
            except Exception:
                # Catch the error because the external template is noncritical.
                # TODO: Add error reporting here.
                pass

        super(BaseController, self).__init__(self, *args, **kwargs)

    def update_external_template(self, tmpl_url, tmpl_name, timeout):
        """Conditionally fetch and cache the remote template.

        This method will only work on *nix systems.

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
        statinfo = os.stat(tmpl_path)[:10]
        st_mode, st_ino, st_dev, st_nlink,\
            st_uid, st_gid, st_size, st_ntime,\
            st_mtime, st_ctime = statinfo

        # st_mtime and now are both unix timestamps.
        now = time.time()
        diff = now - st_mtime

        # if the template file is less than 5 minutes old, return
        if diff < timeout:
            return False

        try:
            # If the tmpl_tmp_path file exists
            # That means that another instance of simpleplex is writing to it
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
