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
from mediaplex.model import DBSession, fetch_row, Media, Audio, Video, PlaceholderMedia, MediaFile, Podcast, Comment, Tag, Author, AuthorWithIP
from mediaplex.model.media import change_media_type
from mediaplex.forms.admin import SearchForm, AlbumArtForm
from mediaplex.forms.media import MediaForm, AddFileForm, EditFileForm, UpdateStatusForm, PodcastFilterForm
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

        form = MediaForm(action=url_for(action='save'), media=media)
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
        if tmpl_context.action == 'save':
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
            update_status_form = UpdateStatusForm(action=url_for(action='update_status')),
        )


    @expose()
    @validate(MediaForm(), error_handler=edit)
    def save(self, id, slug, title, author_name, author_email,
             description, notes, details, podcast, tags, delete=None, **kwargs):
        if id == 'new':
            media = PlaceholderMedia()
        else:
            media = fetch_row(Media, id, incl_trash=True)

        if delete:
            media.status.add('trash')
            DBSession.add(media)
            DBSession.flush()
            redirect(action='index')

        media.slug = slug
        media.title = title
        media.author = Author(author_name, author_email)
        media.description = clean_xhtml(description)
        media.notes = notes
        media.duration = helpers.duration_to_seconds(details['duration'])

        if (podcast and not media.podcast_id and 'publish' in media.status \
            and not any(True for file in media.files if file.enable_feed)):
            media.status.remove('publish')
            media.status.add('unencoded')
            media.publish_on = None
        media.podcast_id = podcast

        if id == 'new':
            DBSession.add(media)
            DBSession.flush()
        media.set_tags(tags)

        DBSession.add(media)
        DBSession.flush()

        if isinstance(media, PlaceholderMedia) and media.files:
            media_type = media.files[0].av
            DBSession.expire(media)
            change_media_type(media.id, media_type)
            media = DBSession.query(Media).get(media.id)

        media.update_status()
        DBSession.add(media)
        DBSession.flush()

        redirect(action='edit', id=media.id)


    @expose('json')
    @validate(AddFileForm(), error_handler=edit)
    def add_file(self, id, file=None, url=None, **kwargs):
        if id == 'new':
            media = PlaceholderMedia()
            media.slug = 'upload-%s' % datetime.now()
            media.title = 'Placeholder (%s)' % datetime.now()
            media.author = Author('FIXME', 'FIXME@FIXME.com')
            DBSession.add(media)
            DBSession.flush()
        else:
            media = fetch_row(Media, id, incl_trash=True)
        media_file = MediaFile()

        if file is not None:
            # Save the uploaded file
            media_file.type = os.path.splitext(file.filename)[1].lower()[1:]
            media_file.url = str(media.id) + '-' + media.slug + '.' + media_file.type
            permanent_path = os.path.join(config.media_dir, media_file.url)
            permanent_file = open(permanent_path, 'w')
            copyfileobj(file.file, permanent_file)
            file.file.close()
            media_file.size = os.fstat(permanent_file.fileno())[6]
            permanent_file.close()

        elif url:
            # Parse the URL checking for known embeddables like YouTube
            for type, info in config.embeddable_filetypes.iteritems():
                match = re.match(info['pattern'], url)
                if match:
                    media_file.type = type
                    media_file.url = match.group('id')
                    media_file.enable_feed = False
                    break
            else:
                media_file.type = os.path.splitext(url)[1].lower()[1:]
                media_file.url = url

        media.files.append(media_file)
        DBSession.add(media)
        DBSession.flush()

        if isinstance(media, PlaceholderMedia) and len(media.files) == 1:
            # We've added the 1st file to a placeholder so set it to Audio or Video
            DBSession.expire(media)
            change_media_type(media.id, media_file.av)
            DBSession.flush()
            media = DBSession.query(Media).get(media.id)

        media.update_status()
        DBSession.add(media)
        DBSession.flush()

        edit_form = EditFileForm(action=url_for(action='edit_file'))
        edit_form_xhtml = unicode(edit_form.display(file=media_file))

        status_form = UpdateStatusForm(action=url_for(action='update_status'))
        status_form_xhtml = unicode(status_form.display(media=media))

        return dict(
            success = True,
            media_id = media.id,
            file_id = media_file.id,
            edit_form = edit_form_xhtml,
            status_form = status_form_xhtml,
        )


    @expose('json')
    @validate(validators={'file_id': validators.Int(),
                          'prev_id': validators.Int()})
    def reorder_file(self, id, file_id, prev_id, **kwargs):
        media = fetch_row(Media, id, incl_trash=True)
        q = media.files.reposition(file_id, prev_id)
        DBSession.flush()
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
            DBSession.flush()
            DBSession.expire(media, ['files'])
            if len(media.files) == 0:
                # We've deleted the last file so this media is now a placeholder
                DBSession.expire(media)
                media.status.update('unencoded,unreviewed,draft')
                DBSession.add(media)
                DBSession.flush()
                change_media_type(media.id, PlaceholderMedia)
                media = DBSession.query(Media).get(media.id)

        media.update_status()
        DBSession.add(media)
        DBSession.flush()

        if request.is_xhr:
            status_form = UpdateStatusForm(action=url_for(action='update_status'))
            status_form_xhtml = unicode(status_form.display(media=media))
            data['status_form'] = status_form_xhtml
            return data
        else:
            redirect(action='edit')


    @expose('json')
    @validate(AlbumArtForm(), error_handler=edit)
    def save_album_art(self, id, album_art, **kwargs):
        if id == 'new':
            media = PlaceholderMedia()
            media.slug = 'upload-%s' % datetime.now()
            media.title = 'Placeholder (%s)' % datetime.now()
            media.author = Author('FIXME', 'FIXME@FIXME.com')
            DBSession.add(media)
            DBSession.flush()
        else:
            media = fetch_row(Media, id, incl_trash=True)

        temp_file = album_art.file
        im_path = '%s/../public/images/media/%d%%s.jpg' % (os.path.dirname(__file__), media.id)

        im = Image.open(temp_file)
        im.resize((162, 113), 1).save(im_path % 's')
        im.resize((240, 168), 1).save(im_path % 'm')
        im.resize((410, 273), 1).save(im_path % 'l')

        return dict(
            success = True,
            media_id = media.id,
        )


    @expose()
    @validate(UpdateStatusForm(), error_handler=edit)
    def update_status(self, id, update_button, **values):
        media = fetch_row(Media, id, incl_trash=True)

        if update_button == 'Review Complete':
            # FIXME view shouldn't display this button if there are no files added
            media.status.discard('unreviewed')

        elif update_button == 'Publish Now':
            # FIXME should check that there is a file here
            media.status.discard('draft')
            media.status.add('publish')
            media.publish_on = datetime.now()

        media.update_status()
        DBSession.add(media)
        DBSession.flush()

        status_form = UpdateStatusForm(action=url_for(action='update_status'))
        status_form_xhtml = unicode(status_form.display(media=media))
        return status_form_xhtml
