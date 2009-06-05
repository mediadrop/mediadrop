"""
Video/Media Admin Controller
"""
import os.path
from urlparse import urlparse, urlunparse
from cgi import parse_qs
from PIL import Image
from datetime import datetime
from tg import config, flash, url, request, redirect
from tg.decorators import paginate, expose, validate, require
from sqlalchemy import and_, or_
from sqlalchemy.orm import eagerload, undefer
from repoze.what.predicates import has_permission
from pylons import tmpl_context

from mediaplex.lib import helpers
from mediaplex.lib.helpers import expose_xhr
from mediaplex.lib.base import RoutingController
from mediaplex.model import DBSession, Video, Comment, Tag, Author, AuthorWithIP
from mediaplex.forms.admin import SearchForm
from mediaplex.forms.video import VideoForm, AlbumArtForm
from mediaplex.forms.comments import PostCommentForm

class VideoadminController(RoutingController):
    """Admin video actions which deal with groups of videos"""
    allow_only = has_permission('admin')

    @expose_xhr('mediaplex.templates.admin.video.index', 'mediaplex.templates.admin.video.index-table')
    @paginate('videos', items_per_page=25)
    def index(self, page=1, search=None, **kw):
        videos = DBSession.query(Video)\
            .filter(Video.status.excludes('trash'))\
            .options(undefer('comment_count'))\
            .order_by(Video.status.desc(), Video.created_on)
        if search is not None:
            like_search = '%%%s%%' % search
            videos = videos.filter(or_(
                Video.title.like(like_search),
                Video.description.like(like_search),
                Video.notes.like(like_search),
                Video.tags.any(Tag.name.like(like_search)),
            ))
        return dict(
            videos=videos,
            search=search,
            search_form=SearchForm(action=helpers.url_for()),
        )

    @expose('mediaplex.templates.admin.video.edit')
    def edit(self, id, **values):
        video = self._fetch_video(id)
        form = VideoForm(action=helpers.url_for(action='save', id=video.id), video=video)
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
                'url': video.url or video.upload_url
            },
        }

        album_art_form_errors = {}
        if tmpl_context.action == 'save_album_art':
            album_art_form_errors = tmpl_context.form_errors

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
            'album_art_form_errors': album_art_form_errors,
            'album_art_form': AlbumArtForm(action=helpers.url_for(action='save_album_art', id=video.id)),
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
            redirect(helpers.url_for(action='index'))

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
        redirect(helpers.url_for(action='edit', id=video.id))

    @expose()
    @validate(AlbumArtForm(), error_handler=edit)
    def save_album_art(self, id, **values):
        video = self._fetch_video(id)
        temp_file = values['album_art'].file
        im_path = '%s/../public/images/videos/%d%%s.jpg' % (os.path.dirname(__file__), video.id)
        im = Image.open(temp_file)
        im.resize((162, 113), 1).save(im_path % 's')
        im.resize((240, 168), 1).save(im_path % 'm')
        redirect(helpers.url_for(action='edit', id=video.id))

    @expose('mediaplex.templates.admin.video.update-status-form')
    def update_status(self, id, update_button, **values):
        video = self._fetch_video(id)
        error = None

        if update_button == 'Review Complete':
            video.status.discard('pending_review')

        elif update_button == 'Encoding Complete':
            if video.upload_url and not video.url:
                orig_name, orig_ext = os.path.splitext(video.upload_url)
                flv_file = '%s.%s' % (orig_name, 'flv')
                flv_path = os.path.join(config.media_dir, flv_file)
                if os.path.exists(flv_path):
                    video.url = flv_file
                    video.status.discard('pending_encoding')
                else:
                    error = u'Encoded video not found, please upload and name it: %s' % flv_file
            elif video.url and video.url.endswith('.flv'):
                video.status.discard('pending_encoding')
            elif video.url and not video.upload_url:
                video.status.discard('pending_encoding')
                error = u'Encoding unnecessary.'
            else:
                error = u'Video record does not match the status.'

        elif update_button == 'Publish Now':
            video.status.discard('draft')
            video.status.add('publish')
            video.publish_on = datetime.now()

        else:
            error = u'No action to perform'

        return dict(video=video, status_error=error)

    def _fetch_video(self, id):
        if id == 'new':
            video = Video()
            video.id = 'new'
        else:
            video = DBSession.query(Video).get(id)
        return video
