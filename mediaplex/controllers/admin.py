from datetime import datetime
from tg import expose, validate, flash, require, url, request, redirect
from sqlalchemy import and_, or_
from sqlalchemy.orm import eagerload

from mediaplex.lib.base import BaseController
from mediaplex.model import DBSession, Media, Video, Comment, Tag
from mediaplex.controllers.video import VideoAdminController

class AdminController(BaseController):

    video = VideoAdminController()

    @expose()
    def default(self, *args):
        redirect('/admin/dashboard')

    @expose('mediaplex.templates.admin.index')
    def dashboard(self):
        # Videos that are unreviewed are 'Awaiting Review'
        video_to_review = DBSession.query(Video).filter(Video.status == 'unreviewed').\
            order_by(Video.created_on)[:6]

        # Any publishable video that doesn't have a publish_on date is
        # 'Awaiting Encoding', whether or not the url is None.
        video_to_encode = DBSession.query(Video).options(eagerload('tags')).\
            filter(Video.status == 'publishable').\
            filter(Video.publish_on == None).order_by(Video.created_on)[:6]

        # Any publishable video that does have a publish_on date that is in the
        # past and is publishable is 'Recently Published'
        recent = DBSession.query(Media).filter(Media.status == 'publishable').\
            filter(Media.url != None).filter(Media.publish_on < datetime.now).\
            order_by(Media.publish_on)[:5]

        comments_to_review = DBSession.query(Comment).filter_by(status='unreviewed').count()
        comments_total = DBSession.query(Comment).count()

        return dict(media_to_review=video_to_review,
                    media_to_encode=video_to_encode,
                    num_comments_to_review=comments_to_review,
                    num_comments_total=comments_total,
                    recent=recent)
