# This file is a part of MediaDrop (http://www.mediadrop.net),
# Copyright 2009-2013 MediaDrop contributors
# For the exact contribution history, see the git revision log.
# The source code contained in this file is licensed under the GPLv3 or
# (at your option) any later version.
# See LICENSE.txt in the main project directory, for more information.
"""
Comment Moderation Controller
"""

from pylons import request
from sqlalchemy import orm

from mediacore.forms.admin import SearchForm
from mediacore.forms.admin.comments import EditCommentForm
from mediacore.lib.auth import has_permission
from mediacore.lib.base import BaseController
from mediacore.lib.decorators import (autocommit, expose, expose_xhr,
    observable, paginate)
from mediacore.lib.helpers import redirect, url_for
from mediacore.model import Comment, Media, fetch_row
from mediacore.model.meta import DBSession
from mediacore.plugin import events

import logging
log = logging.getLogger(__name__)

edit_form = EditCommentForm()
search_form = SearchForm(action=url_for(controller='/admin/comments',
                                        action='index'))

class CommentsController(BaseController):
    allow_only = has_permission('edit')

    @expose_xhr('admin/comments/index.html',
                'admin/comments/index-table.html')
    @paginate('comments', items_per_page=25)
    @observable(events.Admin.CommentsController.index)
    def index(self, page=1, search=None, media_filter=None, **kwargs):
        """List comments with pagination and filtering.

        :param page: Page number, defaults to 1.
        :type page: int
        :param search: Optional search term to filter by
        :type search: unicode or None
        :param media_filter: Optional media ID to filter by
        :type media_filter: int or None
        :rtype: dict
        :returns:
            comments
                The list of :class:`~mediacore.model.comments.Comment` instances
                for this page.
            edit_form
                The :class:`mediacore.forms.admin.comments.EditCommentForm` instance,
                to be rendered for each instance in ``comments``.
            search
                The given search term, if any
            search_form
                The :class:`~mediacore.forms.admin.SearchForm` instance
            media_filter
                The given podcast ID to filter by, if any
            media_filter_title
                The media title for rendering if a ``media_filter`` was specified.

        """
        comments = Comment.query.trash(False)\
            .order_by(Comment.reviewed.asc(),
                      Comment.created_on.desc())

        # This only works since we only have comments on one type of content.
        # It will need re-evaluation if we ever add others.
        comments = comments.options(orm.eagerload('media'))

        if search is not None:
            comments = comments.search(search)

        media_filter_title = media_filter
        if media_filter is not None:
            comments = comments.filter(Comment.media.has(Media.id == media_filter))
            media_filter_title = DBSession.query(Media.title).get(media_filter)
            media_filter = int(media_filter)

        return dict(
            comments = comments,
            edit_form = edit_form,
            media_filter = media_filter,
            media_filter_title = media_filter_title,
            search = search,
            search_form = search_form,
        )

    @expose('json', request_method='POST')
    @autocommit
    @observable(events.Admin.CommentsController.save_status)
    def save_status(self, id, status, ids=None, **kwargs):
        """Approve or delete a comment or comments.

        :param id: A :attr:`~mediacore.model.comments.Comment.id` if we are
            acting on a single comment, or ``"bulk"`` if we should refer to
            ``ids``.
        :type id: ``int`` or ``"bulk"``
        :param status: ``"approve"`` or ``"trash"`` depending on what action
            the user requests.
        :param ids: An optional string of IDs separated by commas.
        :type ids: ``unicode`` or ``None``
        :rtype: JSON dict
        :returns:
            success
                bool
            ids
                A list of :attr:`~mediacore.model.comments.Comment.id`
                that have changed.

        """
        if id != 'bulk':
            ids = [id]
        if not isinstance(ids, list):
            ids = [ids]

        if status == 'approve':
            publishable = True
        elif status == 'trash':
            publishable = False
        else:
            # XXX: This form should never be submitted without a valid status.
            raise AssertionError('Unexpected status: %r' % status)

        comments = Comment.query.filter(Comment.id.in_(ids)).all()

        for comment in comments:
            comment.reviewed = True
            comment.publishable = publishable
            DBSession.add(comment)

        DBSession.flush()

        if request.is_xhr:
            return dict(success=True, ids=ids)
        else:
            redirect(action='index')

    @expose('json', request_method='POST')
    @autocommit
    @observable(events.Admin.CommentsController.save_edit)
    def save_edit(self, id, body, **kwargs):
        """Save an edit from :class:`~mediacore.forms.admin.comments.EditCommentForm`.

        :param id: Comment ID
        :type id: ``int``
        :rtype: JSON dict
        :returns:
            success
                bool
            body
                The edited comment body after validation/filtering

        """
        comment = fetch_row(Comment, id)
        comment.body = body
        DBSession.add(comment)
        return dict(
            success = True,
            body = comment.body,
        )
