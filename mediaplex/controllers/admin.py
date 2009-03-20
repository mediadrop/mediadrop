from tg import expose, validate, flash, require, url, request, redirect
from sqlalchemy import and_, or_
from sqlalchemy.orm import eagerload

from mediaplex.lib.base import BaseController
from mediaplex.model import DBSession, Video, Comment, Tag
from mediaplex.controllers.video import VideoAdminController

class AdminController(BaseController):

    video = VideoAdminController()

    @expose()
    def default(self, *args):
        redirect('/admin/dashboard')

    @expose('mediaplex.templates.admin.index')
    def dashboard(self):
        media_to_review = DBSession.query(Video).filter(Video.status == 'unreviewed').\
            order_by(Video.created_on)[:6]

        media_to_encode = DBSession.query(Video).options(eagerload('tags')).\
            filter(Video.status == 'unreviewed').filter(Video.url == None).\
            order_by(Video.created_on)[:6]

        # TODO - update when date_published is available
        recent = DBSession.query(Video).filter(Video.status.in_(['publishable','draft'])).filter(Video.url != None).\
            order_by(Video.modified_on)[:5]

        comments_to_review = DBSession.query(Comment).filter_by(status='unreviewed').count()
        comments_total = DBSession.query(Comment).count()

        return dict(media_to_review=media_to_review,
                    media_to_encode=media_to_encode,
                    num_comments_to_review=comments_to_review,
                    num_comments_total=comments_total,
                    recent=recent)
