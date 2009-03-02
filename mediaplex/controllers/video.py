from mediaplex.lib.base import BaseController
from tg import expose, validate, flash, require, url, request, redirect
from pylons.i18n import ugettext as _

from mediaplex.model import DBSession, metadata, Video, Comment
from mediaplex.forms.comments import PostCommentForm
from formencode import validators

class VideoController(BaseController):
    @expose('mediaplex.templates.video.grid')
    def grid(self, page=1, **kwargs):
        """Grid-style List Action"""
        return dict(page=self._fetch_page(page, 25))

    @expose('mediaplex.templates.video.mediaflow')
    def flow(self, page=1, **kwargs):
        """Mediaflow List Action"""
        return dict(page=self._fetch_page(page, 9))
    default = flow

    @expose('mediaplex.templates.video.mediaflow-ajax')
    def ajax(self, page=1, **kwargs):
        """Mediaflow Ajax Fetch Action"""
        return dict(page=self._fetch_page(page, 3))

    def _fetch_page(self, page_num=1, items_per_page=25, query=None):
        """Helper method for paginating video results"""
        from webhelpers import paginate
        query = query or DBSession.query(Video)
        return paginate.Page(query, page_num, items_per_page)

    @expose()
    def lookup(self, slug, *remainder):
        video = VideoRowController(slug)
        return video, remainder


class VideoRowController(object):
    def __init__(self, slug):
        self.video = DBSession.query(Video).filter_by(slug=slug).one()

    @expose('mediaplex.templates.video.view')
    def view(self, form=None, **values):
        if form is None:
            form = PostCommentForm(action='/video/%s/comment' % self.video.slug)
        self.video.views += 1
        DBSession.add(self.video)
        return dict(video=self.video, post_comment_form=form)
    default = view

    @expose()
    @validate(validators=dict(rating=validators.Int()))
    def rate(self, rating):
        self.video.add_rating(rating)
        DBSession.add(self.video)
        redirect('/video/%s' % self.video.slug)

    @expose()
    def download(self):
        return 'download video'

    @expose()
    @validate(PostCommentForm(), error_handler=view)
    def comment(self, **values):
        c = Comment()
        c.name = values['name']
        c.subject = 'Re: %s' % self.video.title
        c.body = values['body']
        self.video.comments.append(c)
        DBSession.add(c)
        redirect('/video/%s' % self.video.slug)
