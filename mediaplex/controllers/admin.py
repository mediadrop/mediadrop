from datetime import datetime
from tg import expose, validate, decorators, flash, require, url, request, redirect
from sqlalchemy import and_, or_
from sqlalchemy.orm import eagerload
import webhelpers.paginate
from repoze.what.predicates import has_permission

from mediaplex.lib.base import RoutingController
from mediaplex.lib.helpers import expose_xhr
from mediaplex.model import DBSession, fetch_row, Media, Comment, Tag

class AdminController(RoutingController):
    """Admin dashboard actions"""
    allow_only = has_permission('admin')

    @expose('mediaplex.templates.admin.index')
    def index(self, **kwargs):
        # Any publishable video that does have a publish_on date that is in the
        # past and is publishable is 'Recently Published'
        recent_media = DBSession.query(Media)\
            .filter(Media.status >= 'publish')\
            .filter(Media.publish_on < datetime.now)\
            .order_by(Media.publish_on)[:5]
        comments_unreviewed = DBSession.query(Comment).filter(Comment.status >= 'unreviewed').count()
        comments_total = DBSession.query(Comment).count()

        return dict(
            review_page=self._fetch_page('awaiting_review'),
            encode_page=self._fetch_page('awaiting_encoding'),
            publish_page=self._fetch_page('awaiting_publishing'),
            num_comments_to_review=comments_unreviewed,
            num_comments_total=comments_total,
            recent_media=recent_media
        )

    @expose('mediaplex.templates.admin.media.dash-table')
    def video_table(self, table, page, **kwargs):
        """ShowMore Ajax Fetch Action"""
        return dict(
            media=self._fetch_page(table, page).items,
        )

    def _fetch_page(self, type='awaiting_review', page=1, items_per_page=6):
        """Helper method for paginating media results"""

        query = DBSession.query(Media).order_by(Media.created_on)

        if type == 'awaiting_review':
            query = query.filter(Media.status.intersects('unreviewed')).\
                         filter(Media.status.excludes('trash'))
        elif type == 'awaiting_encoding':
            query = query.filter(Media.status.intersects('unencoded')).\
                         filter(Media.status.excludes('trash,unreviewed'))
        elif type == 'awaiting_publishing':
            query = query.filter(Media.status.issubset('draft'))

        return webhelpers.paginate.Page(query, page, items_per_page)
