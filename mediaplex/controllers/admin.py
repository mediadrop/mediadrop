from datetime import datetime
from tg import expose, validate, flash, require, url, request, redirect
from sqlalchemy import and_, or_
from sqlalchemy.orm import eagerload
from webhelpers import paginate

from mediaplex.lib.base import BaseController
from mediaplex.model import DBSession, Media, Video, Comment, Tag
from mediaplex.controllers.video import VideoAdminController
from mediaplex.controllers.comments import CommentAdminController

class AdminController(BaseController):
    video = VideoAdminController()
    comments = CommentAdminController()

    @expose('mediaplex.templates.admin.index')
    def index(self):
        # Any publishable video that does have a publish_on date that is in the
        # past and is publishable is 'Recently Published'
        recent_media = DBSession.query(Media).\
            filter(Media.status >= 'publish').\
            filter(Media.publish_on < datetime.now).\
            order_by(Media.publish_on)[:5]
        comments_pending_review = DBSession.query(Comment).filter(Comment.status >= 'pending_review').count()
        comments_total = DBSession.query(Comment).count()

        return dict(review_page=self._fetch_review_page(),
                    encode_page=self._fetch_encode_page(),
                    num_comments_to_review=comments_pending_review,
                    num_comments_total=comments_total,
                    recent_media=recent_media)

    @expose('mediaplex.templates.admin.video.dash-table')
    def ajax_review(self, page_num):
        """ShowMore Ajax Fetch Action for Awaiting Review"""
        return dict(collection=self._fetch_review_page(page_num).items, is_ajax=True)

    def _fetch_review_page(self, page_num=1, items_per_page=6):
        """Helper method for paginating video results"""
        query = DBSession.query(Video).filter(Video.status >= 'pending_review').\
            order_by(Video.created_on)
        return paginate.Page(query, page_num, items_per_page)

    @expose('mediaplex.templates.admin.video.dash-table')
    def ajax_encode(self, page_num):
        """ShowMore Ajax Fetch Action for Awaiting Encoding"""
        return dict(collection=self._fetch_encode_page(page_num).items, is_ajax=True)

    def _fetch_encode_page(self, page_num=1, items_per_page=6):
        """Helper method for paginating video results"""
        query = DBSession.query(Video).options(eagerload('tags')).\
            filter(Video.status >= 'pending_encoding').\
            order_by(Video.created_on)
        return paginate.Page(query, page_num, items_per_page)
