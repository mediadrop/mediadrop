import smtplib

from tg import config, request, response, tmpl_context, exceptions

from mediacore.lib.base import (BaseController, url_for, redirect,
    expose, expose_xhr, validate, paginate)
from mediacore.lib import helpers, email


class ErrorController(BaseController):
    """
    Generates error documents as and when they are required.

    The ErrorDocuments middleware forwards to ErrorController when error
    related status codes are returned from the application.

    This behaviour can be altered by changing the parameters to the
    ErrorDocuments middleware in your config/middleware.py file.

    """

    @expose('mediacore.templates.error')
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
        original_request = request.environ['pylons.original_request']
        original_response = request.environ.get('pylons.original_response')
        default_message = ("<p>We're sorry but we weren't able to process "
                           " this request.</p>")

        return dict(
            prefix = request.environ.get('SCRIPT_NAME', ''),
            code = request.params.get('code', original_response.status_int),
            message = request.params.get('message', default_message),
            vars = dict(POST_request=unicode(original_request)[:2048]),
        )

    @expose()
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
        email.send_support_request(email, url, description, get_vars, post_vars)
        redirect('/')
