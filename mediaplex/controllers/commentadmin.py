from tg import expose, validate, flash, require, url, request, redirect
from tg.decorators import paginate
from formencode import validators
from pylons.i18n import ugettext as _
from sqlalchemy import and_, or_
from sqlalchemy.orm import eagerload
from repoze.what.predicates import has_permission

from mediaplex.lib import helpers
from mediaplex.lib.base import RoutingController
from mediaplex.lib.helpers import expose_xhr
from mediaplex.model import DBSession, metadata, Video, Comment, Tag, Author
from mediaplex.forms.admin import SearchForm
from mediaplex.forms.comments import EditCommentForm

class CommentadminController(RoutingController):
    """Admin comment actions which deal with groups of comments"""
    allow_only = has_permission('admin')

    @expose_xhr('mediaplex.templates.admin.comments.index', 'mediaplex.templates.admin.comments.comment-table')
    @paginate('collection', items_per_page=5)
    def index(self, page=1, search=None, **kwargs):
        comments = DBSession.query(Comment).\
            filter(Comment.status.excludes('trash')).\
            order_by(Comment.status.desc(), Comment.created_on)
        if search is not None:
            like_search = '%%%s%%' % (search,)
            comments = comments.filter(or_(
                Comment.subject.like(like_search),
                Comment.body.like(like_search)
            ))

        edit_forms = [EditCommentForm(action=helpers.url_for(action='save', id=c.id)) for c in comments]
        if request.is_xhr:
            return dict(collection=comments, edit_forms=edit_forms)
        else:
            return dict(collection=comments,
                        search_form=SearchForm(action=helpers.url_for()),
                        search=search,
                        edit_forms=edit_forms)

    def _fetch_comment(self, id):
        comment = DBSession.query(Comment).get(id)
        return comment

    @expose()
    def approve(self, id, **kwargs):
        comment = self._fetch_comment(id)
        comment.status.discard('unreviewed')
        comment.status.add('publish')
        DBSession.add(comment)

    @expose()
    def trash(self, id, **kwargs):
        comment = self._fetch_comment(id)
        comment.status.add('trash')
        DBSession.add(comment)

    @expose()
    def save(self, id, **kwargs):
        comment = self._fetch_comment(id)
        comment.body = kwargs['body']
        DBSession.add(comment)
        redirect(helpers.url_for(action='index', id=None))
