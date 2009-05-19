"""
Video/Media Admin Controller
"""
import shutil
import os.path
from urlparse import urlparse, urlunparse
from cgi import parse_qs
from PIL import Image
from datetime import datetime
from tg import expose, validate, decorators, flash, require, url, request, redirect
from formencode import validators
from pylons.i18n import ugettext as _
from sqlalchemy import and_, or_
from sqlalchemy.orm import eagerload
from webhelpers import paginate

from mediaplex.lib import helpers
from mediaplex.lib.helpers import expose_xhr
from mediaplex.lib.base import Controller, BaseController, RoutingController
from mediaplex.model import DBSession, metadata, Video, Comment, Tag, Author, AuthorWithIP
from mediaplex.forms.admin import SearchForm
from mediaplex.forms.video import VideoForm, AlbumArtForm
from mediaplex.forms.comments import PostCommentForm

class VideoadminController(RoutingController):
    """Admin video actions which deal with groups of videos"""

    @expose_xhr('mediaplex.templates.admin.video.index', 'mediaplex.templates.admin.video.index-table')
    def index(self, page_num=1, search=None, **kwargs):
        if request.is_xhr:
            """ShowMore Ajax Fetch Action"""
            return dict(collection=self._fetch_page(search, page_num).items)
        else:
            search_form = SearchForm(action='/admin/video/')
            search_form_values = {
                'search': not search and 'SEARCH...' or search
            }

            return dict(page=self._fetch_page(search),
                        search_form=search_form,
                        search_form_values=search_form_values,
                        search=search)

    def _fetch_page(self, search=None, page_num=1, items_per_page=10):
        """Helper method for paginating video results"""
        videos = DBSession.query(Video).filter(Video.status.excludes('trash'))
        if search is not None:
            like_search = '%%%s%%' % (search,)
            videos = videos.\
                filter(or_(Video.title.like(like_search),
                           Video.description.like(like_search),
                           Video.notes.like(like_search),
                           Video.tags.any(Tag.name.like(like_search))))

        videos = videos.options(eagerload('comments')).\
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
        form = VideoForm(action='/admin/video/%s/save' % self.video.id, video=self.video)
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
            },
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
        if values.has_key('delete'):
            self.video.status.add('trash')
            DBSession.add(self.video)
            DBSession.flush()
            redirect('/admin/video')

        if self.video.id == 'new':
            self.video.id = None

        self.video.slug = values['slug']
        self.video.title = values['title']
        self.video.author = Author(values['author_name'], values['author_email'])
        self.video.description = values['description']
        self.video.notes = values['notes']
        self.video.duration = helpers.duration_to_seconds(values['details']['duration'])
        self.video.set_tags(values['tags'])

        # parse url
        url = urlparse(values['details']['url'], 'http')
        if 'youtube.com' in url[1]:
            if 'youtube.com/watch' in url[1]:
                youtube_id = parse_qs(url[4])['v']
                self.video.url = urlunparse(('http', 'youtube.com', '/v/%s' % youtube_id, '', None, None))
            else:
                self.video.url = values['details']['url']
        else:
            self.video.encode_url = values['details']['url']

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

    @expose('json')
    def update_status(self, **values):
        submitted = values.get('update_status', None)
        if submitted == 'Review Complete':
            self.video.status.discard('pending_review')
            text = 'Encoding Complete'
        elif submitted == 'Encoding Complete':
            self.video.status.discard('pending_encoding')
            text = 'Publish Now'
        elif submitted == 'Publish Now':
            self.video.status.discard('draft')
            self.video.status.add('publish')
            self.video.publish_on = datetime.now()
            text = None
        else:
            raise Exception
        return {'buttonText': text}

