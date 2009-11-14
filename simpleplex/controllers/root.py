from tg import config, request, response, tmpl_context, flash, TGController
from pylons.i18n import _

from simpleplex.lib.base import (BaseController, url_for, redirect,
    expose, expose_xhr, validate, paginate)
from simpleplex.model import (DBSession, fetch_row,
    Podcast, Media, Topic)


class RootController(TGController):
    @expose('simpleplex.templates.project.index')
    def index(self):
        return dict()

    @expose('simpleplex.templates.login')
    def login(self, came_from=url_for('/')):
        login_counter = request.environ['repoze.who.logins']
        if login_counter > 0:
            flash(_('Wrong credentials'), 'warning')

        return dict(
            login_counter = str(login_counter),
            came_from = came_from,
        )

    @expose()
    def post_login(self, came_from=url_for(controller='/admin')):
        if not request.identity:
            login_counter = request.environ['repoze.who.logins'] + 1
            redirect(came_from)

        userid = request.identity['repoze.who.userid']
        flash(_('Welcome back, %s!') % userid)
        redirect(came_from)

    @expose()
    def post_logout(self, came_from=url_for('/')):
        flash(_('We hope to see you soon!'))
        redirect(came_from)

    def __call__(self, environ, start_response):
        """Invoke the Controller"""
        # TGController.__call__ dispatches to the Controller method
        # the request is routed to. This routing information is
        # available in environ['pylons.routes_dict']
        request.identity = request.environ.get('repoze.who.identity')
        tmpl_context.identity = request.identity
        return TGController.__call__(self, environ, start_response)
