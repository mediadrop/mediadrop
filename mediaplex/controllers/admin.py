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
    def dashboard(self, **kwargs):
        # Any publishable video that does have a publish_on date that is in the
        # past and is publishable is 'Recently Published'
        recent = DBSession.query(Media).filter(Media.status == 'publishable').\
            filter(Media.url != None).filter(Media.publish_on < datetime.now).\
            order_by(Media.publish_on)[:5]

        comments_to_review = DBSession.query(Comment).filter_by(status='unreviewed').count()
        comments_total = DBSession.query(Comment).count()

        return dict(review_page=self._fetch_review_page(),
                    encode_page=self._fetch_encode_page(),
                    num_comments_to_review=comments_to_review,
                    num_comments_total=comments_total,
                    recent=recent)

    @expose('mediaplex.templates.admin.video.video-review-table-ajax')
    def ajax_review(self, page_num):
        """ShowMore Ajax Fetch Action for Awaiting Review"""
        return dict(page=self._fetch_review_page(page_num))

    def _fetch_review_page(self, page_num=1, items_per_page=6):
        """Helper method for paginating video results"""
        from webhelpers import paginate

        # Videos that are unreviewed are 'Awaiting Review'
        query = DBSession.query(Video).filter(Video.status == 'unreviewed').\
            order_by(Video.created_on)

        return paginate.Page(query, page_num, items_per_page)

    @expose('mediaplex.templates.admin.video.video-encode-table-ajax')
    def ajax_encode(self, page_num):
        """ShowMore Ajax Fetch Action for Awaiting Encoding"""
        return dict(page=self._fetch_encode_page(page_num))

    def _fetch_encode_page(self, page_num=1, items_per_page=6):
        """Helper method for paginating video results"""
        from webhelpers import paginate

        # Any 'publishable' video that doesn't have a publish_on date or does
        # not have a url is 'Awaiting Encoding'. This allows the setting of a
        # future publish_on date before encoding is complete.
        query = DBSession.query(Video).options(eagerload('tags')).\
            filter(Video.status == 'publishable').\
            filter(or_(Video.publish_on == None, Video.url == None)).order_by(Video.created_on)

        return paginate.Page(query, page_num, items_per_page)
