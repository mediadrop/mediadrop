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

"""
Comment Moderation Controller
"""
from tg import config, request, response, tmpl_context
from repoze.what.predicates import has_permission
from sqlalchemy import orm, sql

from mediacore.lib.base import (BaseController, url_for, redirect,
    expose, expose_xhr, validate, paginate)
from mediacore.model import DBSession, fetch_row, Media, Comment
from mediacore.lib import helpers
from mediacore.forms.admin import SearchForm
from mediacore.forms.comments import EditCommentForm


edit_form = EditCommentForm()
search_form = SearchForm(action=url_for(controller='/commentadmin',
                                        action='index'))

class CommentadminController(BaseController):
    allow_only = has_permission('admin')

    @expose_xhr('mediacore.templates.admin.comments.index',
                'mediacore.templates.admin.comments.index-table')
    @paginate('comments', items_per_page=50)
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
                The :class:`mediacore.forms.comments.EditCommentForm` instance,
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

    @expose('json')
    def save_status(self, id, status, ids=None, **kwargs):
        """Approve or delete a comment or comments.

        :param id: A :attr:`~mediacore.model.comments.Comment.id` if we are
            acting on a single comment, or ``"bulk"`` if we should refer to
            ``ids``.
        :type id: ``int`` or ``"bulk"``
        :param ids: An optional string of IDs separated by commas.
        :type ids: ``unicode`` or ``None``
        :param status: ``"approve"`` or ``"trash"`` depending on what action
            the user requests.
        :rtype: JSON dict
        :returns:
            success
                bool
            ids
                A list of :attr:`~mediacore.model.comments.Comment.id`
                that have changed.

        """
        if id == 'bulk':
            ids = ids.split(',')
        else:
            ids = [id]

        comments = Comment.query.filter(Comment.id.in_(ids)).all()
        publishable = status == 'approve'

        for comment in comments:
            comment.reviewed = True
            comment.publishable = publishable
            DBSession.add(comment)

        DBSession.flush()

        if request.is_xhr:
            return dict(success=True, ids=ids)
        else:
            redirect(action='index')

    @expose('json')
    def save_edit(self, id, body, **kwargs):
        """Save an edit from :class:`~mediacore.forms.comments.EditCommentForm`.

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
        comment.body = helpers.clean_xhtml(body)
        DBSession.add(comment)
        return dict(
            success = True,
            body = comment.body,
        )
