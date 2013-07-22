# This file is a part of MediaCore CE (http://www.mediacorecommunity.org),
# Copyright 2009-2013 MediaCore Inc., Felix Schwarz and other contributors.
# For the exact contribution history, see the git revision log.
# The source code contained in this file is licensed under the GPLv3 or
# (at your option) any later version.
# See LICENSE.txt in the main project directory, for more information.

from mediacore.lib import email as libemail
from mediacore.lib.base import BaseController
from mediacore.lib.decorators import expose, observable
from mediacore.lib.helpers import redirect, clean_xhtml
from mediacore.lib.i18n import _
from mediacore.plugin import events

class ErrorsController(BaseController):
    """Generates error documents as and when they are required.

    The ErrorDocuments middleware forwards to ErrorController when error
    related status codes are returned from the application.

    This behaviour can be altered by changing the parameters to the
    ErrorDocuments middleware in your config/middleware.py file.
    """
    @expose('error.html')
    @observable(events.ErrorController.document)
    def document(self, *args, **kwargs):
        """Render the error document for the general public.

        Essentially, when an error occurs, a second request is initiated for
        the URL ``/error/document``. The URL is set on initialization of the
        :class:`pylons.middleware.StatusCodeRedirect` object, and can be
        overridden in :func:`tg.configuration.add_error_middleware`. Also,
        before this method is called, some potentially useful environ vars
        are set in :meth:`pylons.middleware.StatusCodeRedirect.__call__`
        (access them via :attr:`tg.request.environ`).

        :rtype: Dict
        :returns:
            prefix
                The environ SCRIPT_NAME.
            vars
                A dict containing the first 2 KB of the original request.
            code
                Integer error code thrown by the original request, but it can
                also be overriden by setting ``tg.request.params['code']``.
            message
                A message to display to the user. Pulled from
                ``tg.request.params['message']``.

        """
        request = self._py_object.request
        environ = request.environ
        original_request = environ.get('pylons.original_request', None)
        original_response = environ.get('pylons.original_response', None)
        default_message = '<p>%s</p>' % _("We're sorry but we weren't able "
                                          "to process this request.")

        message = request.params.get('message', default_message)
        message = clean_xhtml(message)

        return dict(
            prefix = environ.get('SCRIPT_NAME', ''),
            code = int(request.params.get('code', getattr(original_response,
                                                          'status_int', 500))),
            message = message,
            vars = dict(POST_request=unicode(original_request)[:2048]),
        )

    @expose(request_method='POST')
    @observable(events.ErrorController.report)
    def report(self, email='', description='', **kwargs):
        """Email a support request that's been submitted on :meth:`document`.

        Redirects back to the root URL ``/``.

        """
        url = ''
        get_vars = post_vars = {}
        for x in kwargs:
            if x.startswith('GET_'):
                get_vars[x] = kwargs[x]
            elif x.startswith('POST_'):
                post_vars[x] = kwargs[x]
        libemail.send_support_request(email, url, description, get_vars, post_vars)
        redirect('/')
