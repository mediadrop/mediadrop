"""The base Controller API

Provides the BaseController class for subclassing.
"""
from tg import TGController, tmpl_context
from tg.render import render
from tg import request
import pylons

from tg.controllers import DecoratedController
from tg.exceptions import (HTTPFound, HTTPNotFound, HTTPException,
    HTTPClientError)

import mediaplex.model as model

from pylons.i18n import _, ungettext, N_
from tw.api import WidgetBunch

class Controller(object):
    """Base class for a web application's controller.

    Currently, this provides positional parameters functionality
    via a standard default method.
    """

class RoutingController(DecoratedController):
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
