from tg import expose, validate, flash, require, url, request
from tg.decorators import paginate
from formencode import validators
from pylons.i18n import ugettext as _
from sqlalchemy import and_, or_
from sqlalchemy.orm import eagerload
from repoze.what.predicates import has_permission

from mediaplex.lib import helpers
from mediaplex.lib.base import RoutingController
from mediaplex.lib.helpers import expose_xhr, redirect, url_for, clean_xhtml
from mediaplex.model import DBSession, metadata, fetch_row, Comment, Tag, Author
from mediaplex.forms.admin import SearchForm
from mediaplex.forms.comments import EditCommentForm


class CommentadminController(RoutingController):
    """Admin comment actions which deal with groups of comments"""
    allow_only = has_permission('admin')

    @expose_xhr('mediaplex.templates.admin.comments.index',
                'mediaplex.templates.admin.comments.index-table')
    @paginate('comments', items_per_page=5)
    def index(self, page=1, search=None, **kwargs):
        comments = DBSession.query(Comment)\
            .filter(Comment.status.excludes('trash'))\
            .order_by(Comment.status.desc(), Comment.created_on)

        if search is not None:
            like_search = '%' + search + '%'
            comments = comments.filter(or_(
                Comment.subject.like(like_search),
                Comment.body.like(like_search),
            ))

        return dict(
            comments = comments,
            edit_form = EditCommentForm(),
            search = search,
            search_form = not request.is_xhr and SearchForm(action=url_for()),
        )


    @expose('json')
    def approve(self, id, **kwargs):
        # FIXME: This method used to return absolutely nothing.
        # Our convention is to return JSON with a 'success' value for all ajax actions.
        # The JS needs to be updated to check for this value.
        comment = fetch_row(Comment, id, incl_trash=True)
        comment.status.discard('unreviewed')
        comment.status.add('publish')
        DBSession.add(comment)
        return dict(success=True)


    @expose('json')
    def trash(self, id, **kwargs):
        # FIXME: This method used to return absolutely nothing.
        # Our convention is to return JSON with a 'success' value for all ajax actions.
        # The JS needs to be updated to check for this value.
        comment = fetch_row(Comment, id, incl_trash=True)
        comment.status.add('trash')
        DBSession.add(comment)
        return dict(success=True)


    @expose('json')
    def save(self, id, **kwargs):
        comment = fetch_row(Comment, id)
        comment.body = clean_xhtml(kwargs['body'])

        DBSession.add(comment)
        return dict(success=True,body=comment.body)
