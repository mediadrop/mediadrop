from tg import expose, validate, flash, require, url, request, redirect
from formencode import validators
from pylons.i18n import ugettext as _
from sqlalchemy import and_, or_
from sqlalchemy.orm import eagerload

from mediaplex.lib import helpers
from mediaplex.lib.base import RoutingController
from mediaplex.lib.helpers import expose_xhr
from mediaplex.model import DBSession, metadata, Video, Comment, Tag, Author
from mediaplex.forms.admin import SearchForm
from mediaplex.forms.comments import EditCommentForm

class CommentadminController(RoutingController):
    """Admin comment actions which deal with groups of comments"""

    @expose_xhr('mediaplex.templates.admin.comments.index', 'mediaplex.templates.admin.comments.comment-table')
    def index(self, page_num=1, search=None, **kwargs):
        page = self._fetch_page(search, page_num)
        edit_forms = [EditCommentForm(action=helpers.url_for(action='save', id=x.id)) for x in page.items]
        if request.is_xhr:
            """ShowMore Ajax Fetch Action"""
            return dict(collection=page.items, edit_forms=edit_forms)
        else:
            search_form = SearchForm(action='/admin/comments/')
            search_form_values = {
                'search': not search and 'SEARCH...' or search
            }
            return dict(page=page,
                        search_form=search_form,
                        search_form_values=search_form_values,
                        search=search,
                        edit_forms=edit_forms)

    def _fetch_page(self, search=None, page_num=1, items_per_page=10):
        """Helper method for paginating comments results"""
        from webhelpers import paginate

        comments = DBSession.query(Comment)
        if search is not None:
            like_search = '%%%s%%' % (search,)
            comments = comments.filter(or_(Comment.subject.like(like_search),
                       Comment.body.like(like_search)))

        comments = comments.filter(Comment.status.excludes('trash')).\
            order_by(Comment.status.desc(), Comment.created_on)

        return paginate.Page(comments, page_num, items_per_page)

    def _fetch_comment(self, id):
        comment = DBSession.query(Comment).get(id)
        return comment

    @expose()
    def approve(self, id, **kwargs):
        comment = self._fetch_comment(id)
        comment.status.discard('pending_review')
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
        comment.body = kwargs['cbody']
        DBSession.add(comment)
        redirect(helpers.url_for(action='index', id=None))
