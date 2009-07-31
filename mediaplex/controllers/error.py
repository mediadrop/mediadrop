import os.path

import paste.fileapp
import tg
from tg import expose, request
from pylons.controllers.util import forward
from pylons.middleware import error_document_template, media_path
from mediaplex.lib.base import RoutingController

import smtplib

class ErrorController(RoutingController):
    """Generates error documents as and when they are required.

    The ErrorDocuments middleware forwards to ErrorController when error
    related status codes are returned from the application.

    This behaviour can be altered by changing the parameters to the
    ErrorDocuments middleware in your config/middleware.py file.
    """

    @expose('mediaplex.templates.error')
    def document(self, *args, **kwargs):
        """Render the error document

        This method is called in a secondary dispatch initiated in
        pylons.middleware.StatusCodeRedirect.__call__()
        This call sets some extra environment variables that you
        might be interested in.

        The dispatch essentially initiates a second request, for the URL
        /error/document

        The URL /error/document is set on initialization of the
        StatusCodeRedirect object, and can be overridden in
        tg.configuration.add_error_middleware()
        """

        resp = tg.request.environ.get('pylons.original_response')
        default_message = ("<p>We're sorry but we weren't able to process "
        " this request.</p>")
        original_request = request.environ['pylons.original_request']


        return dict(
            prefix = tg.request.environ.get('SCRIPT_NAME', ''),
            code = tg.request.params.get('code', resp.status_int),
            message = tg.request.params.get('message', default_message),
            vars = dict(POST_request=original_request[:2048])
        )

    @expose()
    def report(self, **kwargs):
        email = kwargs.get('email', '')
        description = kwargs.get('description', '')
        url = ''
        get_vars = {}
        post_vars = {}
        for x in kwargs:
            if x.startswith('GET_'):
                get_vars[x] = kwargs[x]
            elif x.startswith('POST_'):
                post_vars[x] = kwargs[x]

        self._send_notification(email, description, url, get_vars, post_vars)

    def _send_notification(self, email, description, url, get_vars, post_vars):
        server=smtplib.SMTP('localhost')
        fr = 'noreply@tmcyouth.com'
        to = ['anthony@simplestation.com']
        subject = 'New Support Request: %s' % email
        body = """A user has asked for support

Email: %s

URL: %s

Description: %s

GET_VARS:
  %s


POST_VARS:
  %s
""" % (
        email,
        url,
        description,
        "\n\n  ".join([x + " :  " + get_vars[x] for x in get_vars]),
        "\n\n  ".join([x + " :  " + post_vars[x] for x in post_vars])
        )

        msg = """To: %s
From: %s
Subject: %s

%s
""" % (", ".join(to), fr, subject, body)

        server.sendmail(fr, to, msg)
        server.quit()

