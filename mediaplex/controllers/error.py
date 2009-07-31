import os.path

import paste.fileapp
import tg
from tg import expose
from pylons.controllers.util import forward
from pylons.middleware import error_document_template, media_path
from mediaplex.lib.base import RoutingController

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
        return dict(
            prefix = tg.request.environ.get('SCRIPT_NAME', ''),
            code = tg.request.params.get('code', resp.status_int),
            message = tg.request.params.get('message', default_message)
        )

