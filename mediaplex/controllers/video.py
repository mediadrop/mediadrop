from datetime import datetime
from tg import expose, validate, flash, require, url, request, redirect
from formencode import validators
from pylons.i18n import ugettext as _
from sqlalchemy import and_, or_
from sqlalchemy.orm import eagerload

from mediaplex.model import DBSession, metadata, Video, Comment, Tag, Author
from mediaplex.lib.base import BaseController
from mediaplex.forms.video import VideoForm
from mediaplex.forms.comments import PostCommentForm


class VideoController(BaseController):
    """Video list actions"""

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
        return VideoRowController(slug), remainder


class VideoRowController(object):
    """Actions specific to a single video"""

    def __init__(self, slug):
        """Pull the video from the database for all actions"""
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
    @validate(PostCommentForm(), error_handler=view)
    def comment(self, **values):
        from tg.exceptions import HTTPSeeOther
        c = Comment()
        c.author = Author(values['name'])
        c.subject = 'Re: %s' % self.video.title
        c.body = values['body']
        self.video.comments.append(c)
        DBSession.add(c)
        raise HTTPSeeOther('/video/%s' % self.video.slug)

    @expose()
    def download(self):
        return 'download video'


class VideoAdminController(BaseController):
    """Admin video actions which deal with groups of videos"""

    @expose('mediaplex.templates.admin.video.index')
    def index(self, search_string=None):
        videos = DBSession.query(Video)
        if search_string is not None:
            like_search = '%%%s%%' % (search_string,)
            videos = videos.outerjoin(Video.tags).\
                filter(or_(Video.title.like(like_search),
                           Video.description.like(like_search),
                           Video.notes.like(like_search),
                           Video.tags.any(Tag.name.like(like_search))))

        # TODO - order by status
        videos = videos.options(eagerload('tags'), eagerload('comments')).\
                    order_by(Video.status.desc(), Video.created_on)[:15]
        return dict(videos=videos,
                    search_string=search_string,
                    datetime_now=datetime.now())

    @expose()
    def lookup(self, slug, *remainder):
        video = VideoRowAdminController(slug)
        return video, remainder


class VideoRowAdminController(object):
    """Admin video actions which deal with a single video"""

    def __init__(self, slug):
        """Pull the video from the database for all actions"""
        self.video = DBSession.query(Video).filter_by(slug=slug).one()

    @expose('mediaplex.templates.admin.video.edit')
    def edit(self, **values):
        form = VideoForm(action='/video/%s/edit_save' % self.video.slug)
        return dict(video=self.video, form=form)

    @expose()
    @validate(VideoForm(), error_handler=edit)
    def edit_save(self, **values):
        print values
