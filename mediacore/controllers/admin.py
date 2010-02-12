# This file is a part of MediaCore, Copyright 2009 Simple Station Inc.
#
# MediaCore is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# MediaCore is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

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
        recent_media = Media.query.published()\
            .order_by(Media.publish_on.desc())[:5]

        comment_count = DBSession.query(Comment).count()
        comment_count_published = DBSession.query(Comment)\
            .filter_by(publishable=True).count()
        comment_count_unreviewed = DBSession.query(Comment)\
            .filter_by(reviewed=False).count()
        comment_count_trash = DBSession.query(Comment)\
            .filter_by(reviewed=True, publishable=False).count()

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
        query = Media.query.order_by(Media.modified_on.desc())

        if type == 'awaiting_review':
            query = query.filter_by(reviewed=False)
        elif type == 'awaiting_encoding':
            query = query.filter_by(reviewed=True, encoded=False)
        elif type == 'awaiting_publishing':
            query = query.filter_by(reviewed=True, encoded=True, publishable=False)

        return webhelpers.paginate.Page(query, page, items_per_page)
