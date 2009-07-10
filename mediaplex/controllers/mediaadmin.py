"""
Media Admin Controller
"""
import os
import re
from shutil import copyfileobj
from urlparse import urlparse, urlunparse
from cgi import parse_qs
from PIL import Image
from datetime import datetime
from copy import copy
from tg import config, flash, url, request
from tg.decorators import paginate, expose, validate, require
from sqlalchemy import and_, or_
from sqlalchemy.orm import eagerload, undefer
from repoze.what.predicates import has_permission
from pylons import tmpl_context
from tw.forms import validators

from mediaplex.lib import helpers
from mediaplex.lib.helpers import expose_xhr, redirect, url_for, clean_xhtml
from mediaplex.lib.base import RoutingController
from mediaplex.model import DBSession, fetch_row, Media, MediaFile, Podcast, Comment, Tag, Author, AuthorWithIP
from mediaplex.forms.admin import SearchForm, AlbumArtForm
from mediaplex.forms.media import MediaForm, AddFileForm, EditFileForm, PodcastFilterForm
from mediaplex.forms.comments import PostCommentForm


class MediaadminController(RoutingController):
#    allow_only = has_permission('admin')

    @expose_xhr('mediaplex.templates.admin.media.index',
                'mediaplex.templates.admin.media.index-table')
    @paginate('media', items_per_page=25)
    def index(self, page=1, search=None, podcast_filter=None, **kw):
        media = DBSession.query(Media)\
            .filter(Media.status.excludes('trash'))\
            .options(undefer('comment_count'))\
            .order_by(Media.status.desc(), Media.publish_on, Media.created_on)

        if search is not None:
            like_search = '%' + search + '%'
            media = media.filter(or_(
                Media.title.like(like_search),
                Media.description.like(like_search),
                Media.notes.like(like_search),
                Media.tags.any(Tag.name.like(like_search)),
            ))

        podcast_filter_title = podcast_filter
        if podcast_filter == 'Unfiled':
            media = media.filter(~Media.podcast.has())
        elif podcast_filter is not None and podcast_filter != 'All Media':
            media = media.filter(Media.podcast.has(Podcast.id == podcast_filter))
            podcast_filter_title = DBSession.query(Podcast.title).get(podcast_filter)
            podcast_filter = int(podcast_filter)

        return dict(
            media = media,
            podcast_filter = podcast_filter,
            podcast_filter_title = podcast_filter_title,
            podcast_filter_form = not request.is_xhr and PodcastFilterForm(action=url_for()),
            search = search,
            search_form = not request.is_xhr and SearchForm(action=url_for()),
        )


    @expose('mediaplex.templates.admin.media.edit')
    @validate(validators={'podcast': validators.Int()})
    def edit(self, id, **values):
        media = fetch_row(Media, id, incl_trash=True)

        if id == 'new':
            media.status = 'unreviewed,unencoded,draft'

        form = MediaForm(action=url_for(action='save_meta'), media=media)
        form_values = {
            'podcast': media.podcast_id,
            'slug': media.slug,
            'title': media.title,
            'author_name': media.author.name,
            'author_email': media.author.email,
            'description': media.description,
            'tags': ', '.join((tag.name for tag in media.tags)),
            'notes': media.notes,
            'details': {
                'duration': helpers.duration_from_seconds(media.duration),
            },
        }
        if tmpl_context.action == 'save_meta':
            form_values.update(values)
        elif id == 'new' and 'podcast' in values:
            form_values['podcast'] = values['podcast']

        album_art_form = AlbumArtForm(action=url_for(action='save_album_art'))
        album_art_form_errors = {}
        if tmpl_context.action == 'save_album_art':
            # In case saving album art failed and we're the error_handler, pass the errors too:
            album_art_form_errors = tmpl_context.form_errors

        file_form = AddFileForm(action=url_for(action='add_file'))
        file_form_values = {}
        if tmpl_context.action == 'save_file':
            file_form_values = values

        file_edit_form = EditFileForm(action=url_for(action='edit_file'))

        return dict(
            media = media,
            form = form,
            form_values = form_values,
            file_form = file_form,
            file_form_values = file_form_values,
            file_edit_form = file_edit_form,
            album_art_form = album_art_form,
            album_art_form_errors = album_art_form_errors,
        )


    @expose()
    @validate(MediaForm(), error_handler=edit)
    def save_meta(self, id, **values):
        media = fetch_row(Media, id, incl_trash=True)

        if str(id) == 'new':
            media.id = 'new'
        elif values.has_key('delete'):
            media.status.add('trash')
            DBSession.add(media)
            DBSession.flush()
            redirect(action='index')

        media.slug = values['slug']
        media.title = values['title']
        media.author = Author(values['author_name'], values['author_email'])
        media.description = clean_xhtml(values['description'])

        media.notes = values['notes']
        media.duration = helpers.duration_to_seconds(values['details']['duration'])
        media.set_tags(values['tags'])
        media.podcast_id = values['podcast']

        DBSession.add(media)
        DBSession.flush()
        redirect(action='edit', id=media.id)


    @expose('json')
    @validate(AddFileForm(), error_handler=edit)
    def add_file(self, id, file=None, url=None, **kwargs):
        media = fetch_row(Media, id, incl_trash=True)
        media_file = MediaFile()

        if file is not None:
            """Save the uploaded file"""
            media_file.type = os.path.splitext(file.filename)[1].lower()[1:]
            media_file.url = str(media.id) + '-' + media.slug + '.' + media_file.type
            permanent_path = os.path.join(config.media_dir, media_file.url)
            permanent_file = open(permanent_path, 'w')
            copyfileobj(file.file, permanent_file)
            file.file.close()
            media_file.size = os.fstat(permanent_file.fileno())[6]
            permanent_file.close()

        elif url:
            """Parse the URL checking for known embeddables like YouTube"""
            for type, info in config.embeddable_filetypes.iteritems():
                match = re.match(info['pattern'], url)
                if match:
                    media_file.type = type
                    media_file.url = match.group('id')
                    break
            else:
                media_file.type = os.path.splitext(url)[1].lower()[1:]
                media_file.url = url

        else:
            raise Exception, 'FAIL'

        media.files.append(media_file)
        DBSession.add(media)
        DBSession.flush()

        edit_form = EditFileForm(action=url_for(action='edit_file'))
        return dict(
            success = True,
            file_id = media_file.id,
            edit_form = unicode(edit_form.display(file=media_file)),
        )


    @expose('json')
    def reorder_file(self, id, file_id, prev_id):
        media = fetch_row(Media, id, incl_trash=True)
        return dict(success=True)


    @expose('json')
    @validate(EditFileForm(), error_handler=edit)
    def edit_file(self, id, file_id, player_enabled, feed_enabled,
                  toggle_player=None, toggle_feed=None, delete=None, **kwargs):
        media = fetch_row(Media, id, incl_trash=True)
        file = [file for file in media.files if file.id == file_id][0]
        data = dict(success=True)

        if toggle_player:
            if file.enable_player == player_enabled:
                file.enable_player = not file.enable_player
                DBSession.add(file)
            data['field'] = 'player_enabled'
            data['value'] = file.enable_player

        elif toggle_feed:
            if file.enable_feed == feed_enabled:
                file.enable_feed = not file.enable_feed
                DBSession.add(file)
            data['field'] = 'feed_enabled'
            data['value'] = file.enable_feed

        elif delete:
            data['field'] = 'delete'
            DBSession.delete(file)

        if request.is_xhr:
            return data
        else:
            redirect(action='edit')



    @expose()
    @validate(AlbumArtForm(), error_handler=edit)
    def save_album_art(self, id, **values):
        media = fetch_row(Media, id, incl_trash=True)
        temp_file = values['album_art'].file
        im_path = '%s/../public/images/media/%d%%s.jpg' % (os.path.dirname(__file__), media.id)
        im = Image.open(temp_file)
        im.resize((162, 113), 1).save(im_path % 's')
        im.resize((240, 168), 1).save(im_path % 'm')
        im.resize((410, 273), 1).save(im_path % 'l')
        redirect(action='edit')


    @expose('mediaplex.templates.admin.media.update-status-form')
    def update_status(self, id, update_button, **values):
        media = fetch_row(Media, id, incl_trash=True)
        error = None

        if update_button == 'Review Complete':
            # FIXME view shouldn't display this button if there are no files added
            media.status.discard('unreviewed')

        elif update_button == 'Encoding Complete':
            # FIXME: Remove this button
            original = [f for f in media.files if f.is_original][0]

            if original.type == media.ENCODED_TYPE:
                media.status.discard('unencoded') # dumb data -- already encoded
            else:
                orig_name, orig_ext = os.path.splitext(original.url)
                encoded_url = '%s.%s' % (orig_name, media.ENCODED_TYPE)
                encoded_path = os.path.join(config.media_dir, encoded_url)
                if os.path.exists(encoded_path):
                    encoded_file = MediaFile()
                    encoded_file.type = media.ENCODED_TYPE
                    encoded_file.url = encoded_url
                    encoded_file.size = os.stat(encoded_path)[6]
                    media.files.append(encoded_file)
                    media.status.discard('unencoded')
                else:
                    error = u'Encoded media not found, please upload and name it: %s' % encoded_url

        elif update_button == 'Publish Now':
            # FIXME should check that there is a file here
            media.status.discard('draft')
            media.status.add('publish')
            media.publish_on = datetime.now()

        else:
            error = u'No action to perform'

        return dict(
            media = media,
            status_error = error,
        )
