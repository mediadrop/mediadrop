"""
Video Media Controllers

"""
import shutil
import os.path
from urlparse import urlparse, urlunparse
from cgi import parse_qs
from PIL import Image
from datetime import datetime
from tg import expose, validate, flash, require, url, request, redirect
from formencode import validators
from pylons.i18n import ugettext as _
from sqlalchemy import and_, or_
from sqlalchemy.orm import eagerload
from webhelpers import paginate

from mediaplex.lib import helpers
from mediaplex.lib.base import Controller, BaseController, RoutingController
from mediaplex.model import DBSession, metadata, Video, Comment, Tag, Author, AuthorWithIP
from mediaplex.model.media import PUBLISHED, AWAITING_ENCODING, AWAITING_REVIEW
from mediaplex.forms.admin import SearchForm
from mediaplex.forms.video import VideoForm
from mediaplex.forms.video import VideoForm, AlbumArtForm
from mediaplex.forms.comments import PostCommentForm

class VideoController(RoutingController):
    """Public video list actions"""

    @expose('mediaplex.templates.video.index')
    def index(self, page=1, **kwargs):
        """Grid-style List Action"""
        return dict(page=self._fetch_page(page, 25))

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
        c.author = AuthorWithIP(values['name'], None, request.environ['REMOTE_ADDR'])
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
    def index(self, **kwargs):
        search_query = kwargs.get('searchquery', None)
        search_form = SearchForm(action='/admin/video/')
        search_form_values = {
            'searchquery': not search_query and 'SEARCH...' or search_query
        }

        return dict(page=self._fetch_page(search_query),
                    search_form=search_form,
                    search_form_values=search_form_values,
                    search_string=search_query,
                    datetime_now=datetime.now(),
                    published_status=PUBLISHED,
                    awaiting_encoding_status=AWAITING_ENCODING,
                    awaiting_review_status=AWAITING_REVIEW)

    @expose('mediaplex.templates.admin.video.video-table-ajax')
    def ajax(self, page_num, search_string=None):
        """ShowMore Ajax Fetch Action"""
        videos_page = self._fetch_page(search_string, page_num)
        return dict(page=videos_page,
                    datetime_now=datetime.now(),
                    published_status=PUBLISHED,
                    awaiting_encoding_status=AWAITING_ENCODING,
                    awaiting_review_status=AWAITING_REVIEW)

    def _fetch_page(self, search_string=None, page_num=1, items_per_page=30):
        """Helper method for paginating video results"""
        from webhelpers import paginate

        videos = DBSession.query(Video).\
            filter(Video.status.in_([PUBLISHED, AWAITING_ENCODING, AWAITING_REVIEW]))
        if search_string is not None:
            like_search = '%%%s%%' % (search_string,)
            videos = videos.outerjoin(Video.tags).\
                filter(or_(Video.title.like(like_search),
                           Video.description.like(like_search),
                           Video.notes.like(like_search),
                           Video.tags.any(Tag.name.like(like_search))))

        videos = videos.options(eagerload('tags'), eagerload('comments')).\
                    order_by(Video.status.desc(), Video.created_on)

        return paginate.Page(videos, page_num, items_per_page)

    @expose()
    def lookup(self, id, *remainder):
        if id == 'new':
            newvideo = Video()
            newvideo.id = 'new'
            video = VideoRowAdminController(video=newvideo)
        else:
            video = VideoRowAdminController(id)
        return video, remainder

class VideoRowAdminController(object):
    """Admin video actions which deal with a single video"""

    def __init__(self, id=None, video=None):
        """Pull the video from the database for all actions"""
        self.video = video or DBSession.query(Video).get(id)

    @expose('mediaplex.templates.admin.video.edit')
    def edit(self, **values):
        form = VideoForm(action='/admin/video/%s/save' % self.video.id)
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
        if self.video.id == 'new' and not self.video.notes:
            form_values['notes'] = """Bible References: None
S&H References: None
Reviewer: None
License: General Upload"""
        form_values.update(values)
        return {
            'video': self.video,
            'form': form,
            'form_values': form_values,
            'album_art_form': AlbumArtForm(action='/admin/video/%s/save_album_art' % self.video.id),
        }
    default = edit

    @expose()
    @validate(VideoForm(), error_handler=edit)
    def save(self, **values):
        if self.video.id == 'new':
            self.video.id = None

        self.video.slug = values['slug']
        self.video.title = values['title']
        self.video.author = Author(values['author_name'], values['author_email'])
        self.video.description = values['description']
        self.video.notes = values['notes']
        self.video.duration = helpers.duration_to_seconds(values['details']['duration'])
        self.video.set_tags(values['tags'])

        url = urlparse(values['details']['url'], 'http')
        if 'youtube.com' in url[1]:
            if 'youtube.com/watch' in url[1]:
                youtube_id = parse_qs(url[4])['v']
                self.video.url = urlunparse(('http', 'youtube.com', '/v/%s' % youtube_id, '', None, None))
            else:
                self.video.url = values['details']['url']
        else:
            self.video.encode_url = values['details']['url']

        if self.video.id == 'new':
            self.video.id = None

        DBSession.add(self.video)
        DBSession.flush()
        redirect('/admin/video/%d/edit' % self.video.id)

    @expose()
    @validate(AlbumArtForm(), error_handler=edit)
    def save_album_art(self, **values):
        temp_file = values['album_art'].file
        im_path = '%s/../public/images/videos/%d%%s.jpg' % (os.path.dirname(__file__), self.video.id)
        im = Image.open(temp_file)
        im.resize((149,  92), 1).save(im_path % 's')
        im.resize((240, 168), 1).save(im_path % 'm')
        redirect('/admin/video/%d/edit' % self.video.id)
