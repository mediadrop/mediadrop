from datetime import datetime

from tg import config, request, response, tmpl_context
from repoze.what.predicates import has_permission
import webhelpers.paginate

from mediacore.lib.base import (BaseController, url_for, redirect,
    expose, expose_xhr, validate, paginate)
from mediacore.model import DBSession, fetch_row, Media, Comment


class AdminController(BaseController):
    """Admin dashboard actions"""
    allow_only = has_permission('admin')

    @expose('mediacore.templates.admin.index')
    def index(self, **kwargs):
        """List recent and important items that deserve admin attention.

        We do not use the :func:`mediacore.lib.helpers.paginate` decorator
        because its somewhat incompatible with the way we handle ajax
        fetching with :meth:`video_table`. This should be refactored and
        fixed at a later date.

        :rtype: Dict
        :returns:
            review_page
                A :class:`webhelpers.paginate.Page` instance containing
                :term:`unreviewed` :class:`~mediacore.model.media.Media`.
            encode_page
                A :class:`webhelpers.paginate.Page` instance containing
                :term:`unencoded` :class:`~mediacore.model.media.Media`.
            publish_page
                A :class:`webhelpers.paginate.Page` instance containing
                :term:`draft` :class:`~mediacore.model.media.Media`.
            recent_media
                A list of recently published
                :class:`~mediacore.model.media.Media`.
            comment_count
                Total num comments
            comment_count_published
                Total approved comments
            comment_count_unreviewed
                Total unreviewed comments
            comment_count_trash
                Total deleted comments

        """
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


    @expose('mediacore.templates.admin.media.dash-table')
    def media_table(self, table, page, **kwargs):
        """Fetch XHTML to inject when the 'showmore' ajax action is clicked.

        :param table: ``awaiting_review``, ``awaiting_encoding``, or
            ``awaiting_publishing``.
        :type table: ``unicode``
        :param page: Page number, defaults to 1.
        :type page: int
        :rtype: dict
        :returns:
            media
                A list of :class:`~mediacore.model.media.Media` instances.

        """
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
