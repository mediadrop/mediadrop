"""The base Controller API

Provides the BaseController class for subclassing.
"""
from tg import TGController, tmpl_context
from tg.render import render
from tg import request
import pylons
from datetime import datetime as dt, timedelta as td
import os
import time
import urllib2

from tg.controllers import DecoratedController
from tg.exceptions import (HTTPFound, HTTPNotFound, HTTPException,
    HTTPClientError)

import simpleplex.model as model

from pylons.i18n import _, ungettext, N_
from tw.api import WidgetBunch

class Controller(object):
    """Base class for a web application's controller.

    Currently, this provides positional parameters functionality
    via a standard default method.
    """

class RoutingController(DecoratedController):

    def __init__(self, *args, **kwargs):
        """Init method for RoutingController

        In this init function, we fetch a new copy of the php template
        every 5 minutes.
        """
        current_dir = os.path.dirname(__file__)
        self.tmpl_url = 'http://tmcyouth.com/anthonys_genshi_template_2009.html'
        self.tmpl_path = '%s/../templates/php.html' % current_dir
        self.tmpl_tmp_path = '%s/../templates/php_new.html' % current_dir
        self.tmpl_timeout = 600 # seconds

        try:
            self.update_php_template()
        except Exception, e:
            # catch the error, so that the users can at least see the old template
            # TODO: Add error reporting here.
            pass

        DecoratedController.__init__(self, *args, **kwargs)


    def update_php_template(self):
        """ Returns C{True} if template is successfully updated.

        Returns C{False} if update fails due to normal causes (like not being
        necessary), and throws an exception if update fails due to IO problems.
        """

        # Stat the main template file.
        statinfo = os.stat(self.tmpl_path)[:10]
        st_mode, st_ino, st_dev, st_nlink,\
            st_uid, st_gid, st_size, st_ntime,\
            st_mtime, st_ctime = statinfo

        # st_mtime and now are both unix timestamps.
        now = time.time()
        diff = now - st_mtime

        # if the template file is less than 5 minutes old, return
        if diff < self.tmpl_timeout:
            return False

        try:
            # If the self.tmpl_tmp_path file exists
            # That means that another instance of simpleplex is writing to it
            # Return immediately
            os.stat(self.tmpl_tmp_path)
            return False
        except OSError, e:
            # If the stat call failed, create the file. and continue.
            tmpl_file = open(self.tmpl_tmp_path, 'w')

        self._update_php_template(tmpl_file)
        return True


    def _update_php_template(self, tmpl_file):
        # Download the template, replace windows style newlines
        tmpl_contents = urllib2.urlopen(self.tmpl_url)
        s = tmpl_contents.read().replace("\r\n", "\n")
        tmpl_contents.close()

        # Write to the temp template file.
        tmpl_file.write(s)
        tmpl_file.close()

        # Rename the temp file to the main template file
        # NOTE: This only works on *nix, and is only guaranteed to work if the
        #       files are on the same filesystem.
        #       see http://docs.python.org/library/os.html#os.rename
        os.rename(self.tmpl_tmp_path, self.tmpl_path)

    def _perform_call(self, func, args):
        if not args:
            args = {}

        try:
            aname = str(args.get('action', 'lookup'))
            controller = getattr(self, aname)

            # If these are the __before__ or __after__ methods, they will have no decoration property
            # This will make the default DecoratedController._perform_call() method choke
            # We'll handle them just like TGController handles them.
            func_name = func.__name__
            if func_name == '__before__' or func_name == '__after__':
                if func_name == '__before__' and hasattr(controller.im_class, '__before__'):
                    return controller.im_self.__before__(*args)
                if func_name == '__after__' and hasattr(controller.im_class, '__after__'):
                    return controller.im_self.__after__(*args)
                return

            else:
                controller = func
                params = args
                remainder = ''

                # Remove all extraneous Routing related params
                undesirables = [
                    'pylons',
                    'start_response',
                    'environ',
                    'action',
                    'controller'
                ]
                for x in undesirables:
                    params.pop(x, None)

                result = DecoratedController._perform_call(
                    self, controller, params, remainder=remainder)

        except HTTPException, httpe:
            result = httpe
            # 304 Not Modified's shouldn't have a content-type set
            if result.status_int == 304:
                result.headers.pop('Content-Type', None)
            result._exception = True
        return result

class BaseController(TGController):
    """Base class for the root of a web application.

    Your web application should have one of these. The root of
    your application is used to compute URLs used by your app.
    """

    def __call__(self, environ, start_response):
        """Invoke the Controller"""
        # TGController.__call__ dispatches to the Controller method
        # the request is routed to. This routing information is
        # available in environ['pylons.routes_dict']

        request.identity = request.environ.get('repoze.who.identity')
        tmpl_context.identity = request.identity
        return TGController.__call__(self, environ, start_response)
