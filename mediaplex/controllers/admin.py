from mediaplex.lib.base import BaseController
from tg import expose, validate, flash, require, url, request, redirect
from sqlalchemy import and_, or_
import logging

from mediaplex.model import DBSession, Video, Comment
from mediaplex.forms.video import VideoForm
from mediaplex.controllers.video import VideoRowController

class AdminController(BaseController):

    @expose()
    def default(self, searchString='', *args):
        redirect('/admin/dashboard/%s' % searchString)

    @expose('mediaplex.templates.admin.index')
    def dashboard(self, searchString=None):
        media_to_review = DBSession.query(Video).filter(Video.reviewed == False)

        if searchString is not None:
            like_search = '%%%s%%' % (searchString,)
            media_to_review = media_to_review.filter(or_(Video.title.like(like_search),
                                                         Video.description.like(like_search),
                                                         Video.author_name.like(like_search),
                                                         Video.notes.like(like_search)))

        media_to_review = media_to_review[:6]
        media_to_encode = DBSession.query(Video).filter_by(reviewed=True,
                                                           encoded=False)[:6]

        comments_to_review = DBSession.query(Comment).filter_by(reviewed=False).count()
        comments_total = DBSession.query(Comment).count()

        return dict(media_to_review=media_to_review,
                    media_to_encode=media_to_encode,
                    num_comments_to_review=comments_to_review,
                    num_comments_total=comments_total,
                    searchString=searchString)
