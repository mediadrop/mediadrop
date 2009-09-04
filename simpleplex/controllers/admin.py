from datetime import datetime
from tg import expose, validate, decorators, flash, require, url, request, redirect
from sqlalchemy import and_, or_
from sqlalchemy.orm import eagerload
import webhelpers.paginate
from repoze.what.predicates import has_permission

from simpleplex.lib.base import RoutingController
from simpleplex.lib.helpers import expose_xhr
from simpleplex.model import DBSession, fetch_row, Media, Comment, Tag

class AdminController(RoutingController):
    """Admin dashboard actions"""
    allow_only = has_permission('admin')

    @expose('simpleplex.templates.admin.index')
    def index(self, **kwargs):
        # Any publishable video that does have a publish_on date that is in the
        # past and is publishable is 'Recently Published'
        recent_media = DBSession.query(Media)\
            .filter(Media.status >= 'publish')\
            .filter(Media.status.excludes('trash'))\
            .filter(Media.publish_on < datetime.now)\
            .order_by(Media.publish_on.desc())[:5]

        comment_count = DBSession.query(Comment).count()
        comment_count_published = DBSession.query(Comment)\
            .filter(Comment.status >= 'publish')\
            .filter(Comment.status.excludes('trash'))\
            .count()
        comment_count_unreviewed = DBSession.query(Comment)\
            .filter(Comment.status >= 'unreviewed')\
            .filter(Comment.status.excludes('trash'))\
            .count()
        comment_count_trash = DBSession.query(Comment)\
            .filter(Comment.status >= 'trash')\
            .count()

        return dict(
            review_page = self._fetch_page('awaiting_review'),
            encode_page = self._fetch_page('awaiting_encoding'),
            publish_page = self._fetch_page('awaiting_publishing'),
            recent_media = recent_media,
            comment_count = comment_count,
            comment_count_published = comment_count_published,
            comment_count_unreviewed = comment_count_unreviewed,
            comment_count_trash = comment_count_trash,
        )

    @expose('simpleplex.templates.admin.media.dash-table')
    def video_table(self, table, page, **kwargs):
        """ShowMore Ajax Fetch Action"""
        return dict(
            media = self._fetch_page(table, page).items,
        )


    def _fetch_page(self, type='awaiting_review', page=1, items_per_page=6):
        """Helper method for paginating media results"""
        query = DBSession.query(Media).order_by(Media.modified_on.desc())

        if type == 'awaiting_review':
            query = query.filter(Media.status.intersects('unreviewed'))\
                         .filter(Media.status.excludes('trash'))
        elif type == 'awaiting_encoding':
            query = query.filter(Media.status.intersects('unencoded'))\
                         .filter(Media.status.excludes('trash,unreviewed'))
        elif type == 'awaiting_publishing':
            query = query.filter(Media.status.issubset('draft'))

        return webhelpers.paginate.Page(query, page, items_per_page)
