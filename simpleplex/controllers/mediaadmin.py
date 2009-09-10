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

from simpleplex.lib import helpers
from simpleplex.lib.helpers import expose_xhr, redirect, url_for, clean_xhtml
from simpleplex.lib.base import RoutingController
from simpleplex.model import DBSession, fetch_row, get_available_slug, Media, MediaFile, Podcast, Comment, Tag, Author, AuthorWithIP
from simpleplex.model.media import create_media_stub
from simpleplex.forms.admin import SearchForm, AlbumArtForm
from simpleplex.forms.media import MediaForm, AddFileForm, EditFileForm, UpdateStatusForm, PodcastFilterForm
from simpleplex.forms.comments import PostCommentForm
from simpleplex.controllers.media import _add_new_media_file

media_form = MediaForm()
add_file_form = AddFileForm()
edit_file_form = EditFileForm()
album_art_form = AlbumArtForm()
update_status_form = UpdateStatusForm()
search_form = SearchForm(action=url_for(controller='/mediaadmin', action='index'))
podcast_filter_form = PodcastFilterForm(action=url_for(controller='/mediaadmin', action='index'))


class MediaadminController(RoutingController):
    allow_only = has_permission('admin')

    @expose_xhr('simpleplex.templates.admin.media.index',
                'simpleplex.templates.admin.media.index-table')
    @paginate('media', items_per_page=25)
    def index(self, page=1, search=None, podcast_filter=None, **kwargs):
        media = DBSession.query(Media)\
            .filter(Media.status.excludes('trash'))\
            .options(undefer('comment_count_published'))\
            .options(undefer('comment_count_unreviewed'))\
            .order_by(Media.status.desc(), Media.modified_on.desc())

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
            podcast_filter_form = podcast_filter_form,
            search = search,
            search_form = search_form,
        )


    @expose('simpleplex.templates.admin.media.edit')
    @validate(validators={'podcast': validators.Int()})
    def edit(self, id, **kwargs):
        """Display the edit forms, or create a new one if the ID is 'new'.

        This page serves as the error_handler for every kind of edit action,
        if anything goes wrong with them they'll be redirected here.
        """
        media = fetch_row(Media, id, incl_trash=True)

        if tmpl_context.action == 'save' or id == 'new':
            # Use the values from error_handler or GET for new podcast media
            media_values = kwargs
        else:
            # Pull the defaults from the media item
            media_values = dict(
                podcast = media.podcast_id,
                slug = media.slug,
                title = media.title,
                author_name = media.author.name,
                author_email = media.author.email,
                description = media.description,
                tags = ', '.join((tag.name for tag in media.tags)),
                topics = [topic.id for topic in media.topics],
                notes = media.notes,
                details = dict(duration = helpers.duration_from_seconds(media.duration)),
            )

        # Re-verify the state of our Media object in case the data is nonsensical
        if id != 'new':
            media.update_type()
            media.update_status()
            DBSession.add(media)

        return dict(
            media = media,
            media_form = media_form,
            media_action = url_for(action='save'),
            media_values = media_values,
            file_add_form = add_file_form,
            file_add_action = url_for(action='add_file'),
            file_edit_form = edit_file_form,
            file_edit_action = url_for(action='edit_file'),
            album_art_form = album_art_form,
            album_art_action = url_for(action='save_album_art'),
            update_status_form = update_status_form,
            update_status_action = url_for(action='update_status'),
        )


    @expose()
    @validate(media_form, error_handler=edit)
    def save(self, id, slug, title, author_name, author_email,
             description, notes, details, podcast, tags, topics, delete=None, **kwargs):
        """Create or edit the metadata for a media item."""
        media = fetch_row(Media, id, incl_trash=True)

        if delete:
            media.status.add('trash')
            DBSession.add(media)
            DBSession.flush()
            redirect(action='index', id=None)

        if media.id == 'new':
            media.status = 'draft,unencoded,unreviewed'

        media.slug = get_available_slug(Media, slug, media)
        media.title = title
        media.author = Author(author_name, author_email)
        media.description = clean_xhtml(description)
        media.notes = notes
        media.duration = helpers.duration_to_seconds(details['duration'])
        media.podcast_id = podcast
        media.set_tags(tags)
        media.set_topics(topics)

        media.update_status()
        DBSession.add(media)
        DBSession.flush()

        redirect(action='edit', id=media.id)


    @expose('json')
    @validate(add_file_form)
    def add_file(self, id, file=None, url=None, **kwargs):
        if id == 'new':
            media = create_media_stub()
        else:
            media = fetch_row(Media, id, incl_trash=True)

        try:
            if file is not None:
                # Create a media object, add it to the video, and store the file permanently.
                media_file = _add_new_media_file(media, file.filename, file.file)
            elif url:
                media_file = MediaFile()
                # Parse the URL checking for known embeddables like YouTube
                for type, info in config.embeddable_filetypes.iteritems():
                    match = re.match(info['pattern'], url)
                    if match:
                        media_file.type = type
                        media_file.url = match.group('id')
                        media_file.enable_feed = False
                        break
                else:
                    # Check for types we can play ourselves
                    type = os.path.splitext(url)[1].lower()[1:]
                    for playable_types in config.playable_types.intervalues():
                        if type in playable_types:
                            media_file.type = type
                            media_file.url = url
                            break
                    else:
                        raise Exception, 'Unsupported URL %s' % url

            else:
                raise Exception, 'Given no action to perform.'

            media.files.append(media_file)
            media.update_type()
            media.update_status()
            DBSession.add(media)
            DBSession.flush()

            # Render some widgets so the XHTML can be injected into the page
            edit_form_xhtml = unicode(edit_file_form.display(
                action=url_for(action='edit_file'), file=media_file))
            status_form_xhtml = unicode(update_status_form.display(
                action=url_for(action='update_status'), media=media))

            return dict(
                success = True,
                media_id = media.id,
                file_id = media_file.id,
                edit_form = edit_form_xhtml,
                status_form = status_form_xhtml,
            )
        except Exception, e:
            return dict(
                success = False,
                message = e.message,
            )

    @expose('json')
    @validate(validators={'file_id': validators.Int(),
                          'budge_infront_id': validators.Int()})
    def reorder_file(self, id, file_id, budge_infront_id, **kwargs):
        media = fetch_row(Media, id, incl_trash=True)
        media.reposition_file(file_id, budge_infront_id)
        DBSession.add(media)
        DBSession.flush()
        return dict(success=True)


    @expose('json')
    @validate(edit_file_form, error_handler=edit)
    def edit_file(self, id, file_id, player_enabled, feed_enabled,
                  toggle_feed, toggle_player, delete, **kwargs):
        media = fetch_row(Media, id, incl_trash=True)
        data = {}

        try:
            try:
                file = [file for file in media.files if file.id == file_id][0]
            except KeyError:
                raise Exception, 'File does not exist.'

            if toggle_player:
                data['field'] = 'player_enabled'
                file.enable_player = data['value'] = not player_enabled
                DBSession.add(file)
            elif toggle_feed:
                data['field'] = 'feed_enabled'
                file.enable_feed = data['value'] = not feed_enabled
                # Raises an exception if it is the only feed enabled file for
                # an already published podcast episode.
                DBSession.add(file)
            elif delete:
                data['field'] = 'delete'
                DBSession.delete(file)
                media.files.remove(file)
            else:
                raise Exception, 'No action to perform.'

            data['success'] = True
            media.update_type()
            media.update_status()
            DBSession.add(media)
        except Exception, e:
            data['success'] = False
            data['message'] = e.message

        if request.is_xhr:
            # Return the rendered widget for injection
            status_form_xhtml = unicode(update_status_form.display(
                action=url_for(action='update_status'), media=media))
            data['status_form'] = status_form_xhtml
            return data
        else:
            DBSession.flush()
            redirect(action='edit')


    @expose('json')
    @validate(album_art_form, error_handler=edit)
    def save_album_art(self, id, album_art, **kwargs):
        if id == 'new':
            media = create_media_stub()
        else:
            media = fetch_row(Media, id, incl_trash=True)

        im_path = os.path.join(config.image_dir, 'media/%d%%s.%%s' % media.id)

        try:
            # Create jpeg thumbnails
            # TODO: Allow other formats?
            im = Image.open(album_art.file)
            for size in ['ss', 's', 'm', 'l']:
                file_path = im_path % (size, 'jpg')
                im.resize(config.album_art_sizes[size], 1).save(file_path)

            # Backup the original image just for kicks
            orig_type = os.path.splitext(album_art.filename)[1].lower()[1:]
            backup_file = open(im_path % ('orig', orig_type), 'w')
            copyfileobj(album_art.file, backup_file)
            album_art.file.close()
            backup_file.close()

            if id == 'new':
                DBSession.add(media)
                DBSession.flush()

            success = True
            message = None
        except IOError:
            success = False
            message = 'Unsupported image type'
        except Exception, e:
            success = False
            message = e.message

        return dict(
            success = success,
            message = message,
            id = media.id,
        )


    @expose('json')
    @validate(update_status_form, error_handler=edit)
    def update_status(self, id, update_button, **values):
        media = fetch_row(Media, id, incl_trash=True)

        # Make the requested change assuming it will be allowed
        if update_button == 'Review Complete':
            media.status.discard('unreviewed')
        elif update_button == 'Publish Now':
            media.status.discard('draft')
            media.status.add('publish')
            media.publish_on = datetime.now()

        try:
            # Verify the change is valid by re-determining the status
            media.update_status()
            DBSession.add(media)
            DBSession.flush()
            data = dict(success=True)
        except Exception, e:
            data = dict(success=False, message=e.message)

        if request.is_xhr:
            # Return the rendered widget for injection
            status_form_xhtml = unicode(update_status_form.display(
                action=url_for(action='update_status'), media=media))
            data['status_form'] = status_form_xhtml
            return data
        else:
            redirect(action='edit')
