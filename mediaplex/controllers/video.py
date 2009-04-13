"""
Video Media Controllers

"""
from datetime import datetime
from tg import expose, validate, flash, require, url, request, redirect
from formencode import validators
from pylons.i18n import ugettext as _
from sqlalchemy import and_, or_
from sqlalchemy.orm import eagerload
from webhelpers import paginate

from mediaplex.model import DBSession, metadata, Video, Tag, authors, comments
from mediaplex.lib import helpers
from mediaplex.lib.base import Controller, BaseController
from mediaplex.forms.video import VideoForm
from mediaplex.forms.comments import PostCommentForm


class VideoController(BaseController):
    """Public video list actions"""

    @expose('mediaplex.templates.video.grid')
    def grid(self, page=1, **kwargs):
        """Grid-style List Action"""
        return dict(page=self._fetch_page(page, 25))
    default = grid

    @expose('mediaplex.templates.video.mediaflow')
    def flow(self, page=1, **kwargs):
        """Mediaflow Action"""
        return dict(page=self._fetch_page(page, 9))

    @expose('mediaplex.templates.video.mediaflow-ajax')
    def flow_ajax(self, page=1, **kwargs):
        """Mediaflow Ajax Fetch Action"""
        return dict(page=self._fetch_page(page, 6))

    def _fetch_page(self, page_num=1, items_per_page=25, query=None):
        """Helper method for paginating video results"""
        query = query or DBSession.query(Video)
        return paginate.Page(query, page_num, items_per_page)

    @expose()
    def lookup(self, slug, *remainder):
        return VideoRowController(slug), remainder


class VideoRowController(object):
    """Actions specific to a single video"""

    def __init__(self, slug=None, video=None):
        """Pull the video from the database for all actions"""
        self.video = video or DBSession.query(Video).filter_by(slug=slug).one()

    @expose('mediaplex.templates.video.view')
    def view(self, **values):
        self.video.views += 1
        DBSession.add(self.video)
        form = PostCommentForm(action='/video/%s/comment' % self.video.slug)
        return {
            'video': self.video,
            'comment_form': form,
            'form_values': values,
        }
    default = view

    @expose()
    @validate(validators=dict(rating=validators.Int()))
    def rate(self, rating):
        self.video.rating(rating)
        DBSession.add(self.video)
        redirect('/video/%s' % self.video.slug)

    @expose()
    @validate(PostCommentForm(), error_handler=view)
    def comment(self, **values):
        c = comments.Comment()
        c.status = comments.PENDING_REVIEW
        c.author = authors.AuthorWithIP(values['name'], None, request.environ['REMOTE_ADDR'])
        c.subject = 'Re: %s' % self.video.title
        c.body = values['body']
        self.video.comments.append(c)
        DBSession.merge(self.video)
        redirect('/video/%s' % self.video.slug)

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
    def lookup(self, id, *remainder):
        video = VideoRowAdminController(id)
        return video, remainder


class VideoRowAdminController(object):
    """Admin video actions which deal with a single video"""

    def __init__(self, id=None, video=None):
        """Pull the video from the database for all actions"""
        self.video = video or DBSession.query(Video).get(id)

    @expose('mediaplex.templates.admin.video.edit')
    def edit(self, **values):
        form = VideoForm(action='/admin/video/%d/save' % self.video.id)
        form_values = {
            'slug': self.video.slug,
            'title': self.video.title,
            'author_name': self.video.author.name,
            'author_email': self.video.author.email,
            'description': self.video.description,
            'tags': ', '.join([tag.name for tag in self.video.tags]),
            'notes': self.video.notes,
            'details': {
                'duration': helpers.duration_from_seconds(self.video.duration),
                'url': self.video.url
            }
        }
        print form_values
        form_values.update(values)
        print form_values
        return dict(video=self.video, form=form, form_values=form_values)

    @expose()
    @validate(VideoForm(), error_handler=edit)
    def save(self, **values):
        self.video.slug = values['slug']
        self.video.title = values['title']
        self.video.author = authors.Author(values['author_name'], values['author_email'])
        self.video.description = values['description']
        self.video.notes = values['notes']
        self.video.duration = values['details']['duration']
        self.video.url = values['details']['url'] or None
        #set tag
        DBSession.add(self.video)
        redirect('/admin/video/%d/edit' % self.video.id)
