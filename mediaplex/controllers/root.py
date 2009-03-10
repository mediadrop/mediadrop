"""Main Controller"""
from mediaplex.lib.base import BaseController
from mediaplex.controllers.error import ErrorController
from mediaplex.controllers.video import VideoController

from tg import expose, flash, require, url, request, redirect
from pylons.i18n import ugettext as _
#from tg import redirect, validate

from mediaplex import model
from mediaplex.model import DBSession, metadata, Video, Comment

#from catwalk.tg2 import Catwalk
from repoze.what import predicates
from mediaplex.controllers.secure import SecureController

class RootController(BaseController):
#    admin = Catwalk(model, DBSession)
    error = ErrorController()
    video = VideoController()

    @expose('mediaplex.templates.index')
    def index(self):
        redirect('/video')

    @expose('mediaplex.templates.admin.index')
    def admin(self):
        videos_to_review = DBSession.query(Video).filter_by(reviewed=False)
        videos_to_encode = DBSession.query(Video).filter_by(reviewed=True,encoded=False)
        comments_to_review = DBSession.query(Comment).filter_by(reviewed=False)
        return dict(videos_to_review=videos_to_review, videos_to_encode=videos_to_encode)

    @expose('mediaplex.templates.index')
    @require(predicates.has_permission('manage', msg=_('Only for managers')))
    def manage_permission_only(self, **kw):
        return dict(page='managers stuff')

    @expose('mediaplex.templates.index')
    @require(predicates.is_user('editor', msg=_('Only for the editor')))
    def editor_user_only(self, **kw):
        return dict(page='editor stuff')

    @expose('mediaplex.templates.login')
    def login(self, came_from=url('/')):
        login_counter = request.environ['repoze.who.logins']
        if login_counter > 0:
            flash(_('Wrong credentials'), 'warning')
        return dict(page='login', login_counter=str(login_counter),
                    came_from=came_from)

    @expose()
    def post_login(self, came_from=url('/')):
        if not request.identity:
            login_counter = request.environ['repoze.who.logins'] + 1
            redirect(url('/login', came_from=came_from, __logins=login_counter))
        userid = request.identity['repoze.who.userid']
        flash(_('Welcome back, %s!') % userid)
        redirect(came_from)

    @expose()
    def post_logout(self, came_from=url('/')):
        flash(_('We hope to see you soon!'))
        redirect(came_from)
