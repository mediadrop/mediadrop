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
from mediaplex.lib.base import Controller, RoutingController
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

    def _fetch_video(self, id):
        if id == 'new':
            video = Video()
            video.id = 'new'
        else:
            video = DBSession.query(Video).get(id)
        return video

    @expose('mediaplex.templates.admin.video.edit')
    def edit(self, id, **values):
        video = self._fetch_video(id)
        form = VideoForm(action='/admin/video/%s/save' % video.id, video=video)
        form_values = {
            'slug': video.slug,
            'title': video.title,
            'author_name': video.author.name,
            'author_email': video.author.email,
            'description': video.description,
            'tags': ', '.join([tag.name for tag in video.tags]),
            'notes': video.notes,
            'details': {
                'duration': helpers.duration_from_seconds(video.duration),
                'url': video.url
            },
        }
        if video.id == 'new' and not video.notes:
            form_values['notes'] = """Bible References: None
S&H References: None
Reviewer: None
License: General Upload"""
        form_values.update(values)
        return {
            'video': video,
            'form': form,
            'form_values': form_values,
            'album_art_form': AlbumArtForm(action='/admin/video/%s/save_album_art' % video.id),
        }
    default = edit

    @expose()
    @validate(VideoForm(), error_handler=edit)
    def save(self, id, **values):
        video = self._fetch_video(id)
        if values.has_key('delete'):
            video.status.add('trash')
            DBSession.add(video)
            DBSession.flush()
            redirect('/admin/video')

        if video.id == 'new':
            video.id = None

        video.slug = values['slug']
        video.title = values['title']
        video.author = Author(values['author_name'], values['author_email'])
        video.description = values['description']
        video.notes = values['notes']
        video.duration = helpers.duration_to_seconds(values['details']['duration'])
        video.set_tags(values['tags'])

        # parse url
        url = urlparse(values['details']['url'], 'http')
        if 'youtube.com' in url[1]:
            if 'youtube.com/watch' in url[1]:
                youtube_id = parse_qs(url[4])['v']
                video.url = urlunparse(('http', 'youtube.com', '/v/%s' % youtube_id, '', None, None))
            else:
                video.url = values['details']['url']
        else:
            video.encode_url = values['details']['url']

        DBSession.add(video)
        DBSession.flush()
        redirect('/admin/video/%d/edit' % video.id)

    @expose()
    @validate(AlbumArtForm(), error_handler=edit)
    def save_album_art(self, id, **values):
        video = self._fetch_video(id)
        temp_file = values['album_art'].file
        im_path = '%s/../public/images/videos/%d%%s.jpg' % (os.path.dirname(__file__), video.id)
        im = Image.open(temp_file)
        im.resize((149,  92), 1).save(im_path % 's')
        im.resize((240, 168), 1).save(im_path % 'm')
        redirect('/admin/video/%d/edit' % video.id)

    @expose('json')
    def update_status(self, id, **values):
        video = self._fetch_video(id)
        submitted = values.get('update_status', None)
        if submitted == 'Review Complete':
            video.status.discard('pending_review')
            text = 'Encoding Complete'
        elif submitted == 'Encoding Complete':
            video.status.discard('pending_encoding')
            text = 'Publish Now'
        elif submitted == 'Publish Now':
            video.status.discard('draft')
            video.status.add('publish')
            video.publish_on = datetime.now()
            text = None
        else:
            raise Exception
        return {'buttonText': text}

