# This file is a part of MediaDrop (http://www.mediadrop.net),
# Copyright 2009-2013 MediaDrop contributors
# For the exact contribution history, see the git revision log.
# The source code contained in this file is licensed under the GPLv3 or
# (at your option) any later version.
# See LICENSE.txt in the main project directory, for more information.

import webhelpers.paginate

from mediadrop.lib.auth import has_permission
from mediadrop.lib.base import BaseController
from mediadrop.lib.decorators import expose, observable
from mediadrop.model import Comment, Media
from mediadrop.plugin import events

import logging
log = logging.getLogger(__name__)

class IndexController(BaseController):
    """Admin dashboard actions"""
    allow_only = has_permission('edit')

    @expose('admin/index.html')
    @observable(events.Admin.IndexController.index)
    def index(self, **kwargs):
        """List recent and important items that deserve admin attention.

        We do not use the :func:`mediadrop.lib.helpers.paginate` decorator
        because its somewhat incompatible with the way we handle ajax
        fetching with :meth:`video_table`. This should be refactored and
        fixed at a later date.

        :rtype: Dict
        :returns:
            review_page
                A :class:`webhelpers.paginate.Page` instance containing
                :term:`unreviewed` :class:`~mediadrop.model.media.Media`.
            encode_page
                A :class:`webhelpers.paginate.Page` instance containing
                :term:`unencoded` :class:`~mediadrop.model.media.Media`.
            publish_page
                A :class:`webhelpers.paginate.Page` instance containing
                :term:`draft` :class:`~mediadrop.model.media.Media`.
            recent_media
                A list of recently published
                :class:`~mediadrop.model.media.Media`.
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

        return dict(
            review_page = self._fetch_page('awaiting_review'),
            encode_page = self._fetch_page('awaiting_encoding'),
            publish_page = self._fetch_page('awaiting_publishing'),
            recent_media = recent_media,
            comments = Comment.query,
        )


    @expose('admin/media/dash-table.html')
    @observable(events.Admin.IndexController.media_table)
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
                A list of :class:`~mediadrop.model.media.Media` instances.

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
