"""
Media Admin Controller
"""
import os.path
import re
from shutil import copyfileobj
from urlparse import urlparse, urlunparse
from datetime import datetime

from tg import config, request, response, tmpl_context
from repoze.what.predicates import has_permission
from sqlalchemy import orm, sql
from formencode import validators
from PIL import Image

from mediacore.lib.base import (BaseController, url_for, redirect,
    expose, expose_xhr, validate, paginate)
from mediacore.model import (DBSession, fetch_row, get_available_slug,
    Media, MediaFile, Podcast, Tag, Author)
from mediacore.lib import helpers
from mediacore.model.media import create_media_stub
from mediacore.controllers.media import _add_new_media_file
from mediacore.forms.admin import SearchForm, AlbumArtForm
from mediacore.forms.media import (MediaForm, AddFileForm, EditFileForm,
    UpdateStatusForm, PodcastFilterForm)


media_form = MediaForm()
add_file_form = AddFileForm()
edit_file_form = EditFileForm()
album_art_form = AlbumArtForm()
update_status_form = UpdateStatusForm()
search_form = SearchForm(action=url_for(controller='/mediaadmin', action='index'))
podcast_filter_form = PodcastFilterForm(action=url_for(controller='/mediaadmin', action='index'))

class MediaadminController(BaseController):
    allow_only = has_permission('admin')

    @expose_xhr('mediacore.templates.admin.media.index',
                'mediacore.templates.admin.media.index-table')
    @paginate('media', items_per_page=25)
    def index(self, page=1, search=None, podcast_filter=None, **kwargs):
        """List media with pagination and filtering.

        :param page: Page number, defaults to 1.
        :type page: int
        :param search: Optional search term to filter by
        :type search: unicode or None
        :param podcast_filter: Optional podcast to filter by
        :type podcast_filter: int or None
        :rtype: dict
        :returns:
            media
                The list of :class:`~mediacore.model.media.Media` instances
                for this page.
            search
                The given search term, if any
            search_form
                The :class:`~mediacore.forms.admin.SearchForm` instance
            podcast_filter
                The given podcast ID to filter by, if any
            podcast_filter_title
                The podcast name for rendering if a ``podcast_filter`` was specified.
            podcast_filter_form
                The :class:`~mediacore.forms.media.PodcastFilterForm` instance.


        """
        media = DBSession.query(Media)\
            .filter(Media.status.excludes('trash'))\
            .options(orm.undefer('comment_count_published'))\
            .options(orm.undefer('comment_count_unreviewed'))\
            .order_by(Media.status.desc(),
                      Media.publish_on.desc(),
                      Media.modified_on.desc())

        if search is not None:
            like_search = '%' + search + '%'
            media = media.filter(sql.or_(
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


    @expose('mediacore.templates.admin.media.edit')
    @validate(validators={'podcast': validators.Int()})
    def edit(self, id, **kwargs):
        """Display the media forms for editing or adding.

        This page serves as the error_handler for every kind of edit action,
        if anything goes wrong with them they'll be redirected here.

        :param id: Media ID
        :type id: ``int`` or ``"new"``
        :param \*\*kwargs: Extra args populate the form for ``"new"`` media
        :returns:
            media
                :class:`~mediacore.model.media.Media` instance
            media_form
                The :class:`~mediacore.forms.media.MediaForm` instance
            media_action
                ``str`` form submit url
            media_values
                ``dict`` form values
            file_add_form
                The :class:`~mediacore.forms.media.AddFileForm` instance
            file_add_action
                ``str`` form submit url
            file_edit_form
                The :class:`~mediacore.forms.media.EditFileForm` instance
            file_edit_action
                ``str`` form submit url
            album_art_form
                The :class:`~mediacore.forms.admin.AlbumArtForm` instance
            album_art_action
                ``str`` form submit url
            update_status_form
                The :class:`~mediacore.forms.media.UpdateStatusForm` instance
            update_status_action
                ``str`` form submit url

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
        """Save changes or create a new :class:`~mediacore.model.media.Media` instance.

        Form handler the :meth:`edit` action and the
        :class:`~mediacore.forms.media.MediaForm`.

        Redirects back to :meth:`edit` after successful editing
        and :meth:`index` after successful deletion.

        """
        media = fetch_row(Media, id, incl_trash=True)

        if delete:
            media.status.add('trash')
            DBSession.add(media)
            DBSession.flush()
            redirect(action='index', id=None)

        if id == 'new':
            media.status = 'draft,unencoded,unreviewed'

        media.slug = get_available_slug(Media, slug, media)
        media.title = title
        media.author = Author(author_name, author_email)
        media.description = helpers.clean_xhtml(description)
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
        """Save action for the :class:`~mediacore.forms.media.AddFileForm`.

        Creates a new :class:`~mediacore.model.media.MediaFile` from the
        uploaded file or the local or remote URL.

        :param id: Media ID. If ``"new"`` a new Media stub is created with
            :func:`~mediacore.model.media.create_media_stub`.
        :type id: :class:`int` or ``"new"``
        :param file: The uploaded file
        :type file: :class:`cgi.FieldStorage` or ``None``
        :param url: A URL to a recognizable audio or video file
        :type url: :class:`unicode` or ``None``
        :rtype: JSON dict
        :returns:
            success
                bool
            message
                Error message, if unsuccessful
            media_id
                The :attr:`~mediacore.model.media.Media.id` which is
                important if new media has just been created.
            file_id
                The :attr:`~mediacore.model.media.MediaFile.id` for the newly
                created file.
            edit_form
                The rendered XHTML :class:`~mediacore.forms.media.EditFileForm`
                for this file.
            status_form
                The rendered XHTML :class:`~mediacore.forms.media.UpdateStatusForm`

        """
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
                    for playable_types in config.playable_types.itervalues():
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
                action=url_for(action='edit_file', id=media.id),
                file=media_file))
            status_form_xhtml = unicode(update_status_form.display(
                action=url_for(action='update_status', id=media.id),
                media=media))

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
        """Change the position of the given file relative to the 2nd file.

        :param file_id: The file to move
        :type file_id: ``int``
        :param budge_infront_id: The file whos position the first file takes.
            All files behind/after this file are bumped back as well.
        :type budge_infront_id: ``int`` or ``None``
        :rtype: JSON dict
        :returns:
            success
                bool

        """
        media = fetch_row(Media, id, incl_trash=True)
        media.reposition_file(file_id, budge_infront_id)
        DBSession.add(media)
        DBSession.flush()
        return dict(success=True)


    @expose('json')
    @validate(edit_file_form, error_handler=edit)
    def edit_file(self, id, file_id, player_enabled, feed_enabled,
                  toggle_feed, toggle_player, delete, **kwargs):
        """Save action for the :class:`~mediacore.forms.media.EditFileForm`.

        Changes or delets a :class:`~mediacore.model.media.MediaFile`.

        :param id: Media ID
        :type id: :class:`int`
        :rtype: JSON dict
        :returns:
            success
                bool
            message
                Error message, if unsuccessful
            status_form
                Rendered XHTML for the status form, updated to reflect the
                changes made.

        """
        media = fetch_row(Media, id, incl_trash=True)
        data = {}

#        try:
        import mediacore;mediacore.ipython()()
        try:
            file = [file for file in media.files if file.id == file_id][0]
        except IndexError:
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
#        except Exception, e:
#            data['success'] = False
#            data['message'] = e.message

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
        """Save album art uploaded with :class:`~mediacore.forms.media.AlbumArtForm`.

        :param id: Media ID. If ``"new"`` a new Media stub is created with
            :func:`~mediacore.model.media.create_media_stub`.
        :type id: ``int`` or ``"new"``
        :param file: The uploaded file
        :type file: :class:`cgi.FieldStorage` or ``None``
        :rtype: JSON dict
        :returns:
            success
                bool
            message
                Error message, if unsuccessful
            id
                The :attr:`~mediacore.model.media.Media.id` which is
                important if a new media has just been created.

        """
        if id == 'new':
            media = create_media_stub()
        else:
            media = fetch_row(Media, id, incl_trash=True)

        im_path = os.path.join(config.image_dir, 'media/%s%s.%s')

        try:
            # Create thumbnails
            im = Image.open(album_art.file)

            if id == 'new':
                DBSession.add(media)
                DBSession.flush()

            # TODO: Allow other formats?
            for size in ['ss', 's', 'm', 'l']:
                file_path = im_path % (media.id, size, 'jpg')
                im.resize(config.album_art_sizes[size], 1).save(file_path)

            # Backup the original image just for kicks
            orig_type = os.path.splitext(album_art.filename)[1].lower()[1:]
            backup_file = open(im_path % (media.id, 'orig', orig_type), 'w')
            copyfileobj(album_art.file, backup_file)
            album_art.file.close()
            backup_file.close()

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
    def update_status(self, id, update_button=None, publish_on=None, **values):
        """Update the publish status for the given media.

        :param id: Media ID
        :type id: ``int``
        :param update_status: The text of the submit button which indicates
            that the :attr:`~mediacore.model.media.Media.status` should change.
        :type update_status: ``unicode`` or ``None``
        :param publish_on: A date to set to
            :attr:`~mediacore.model.media.Media.publish_on`
        :type publish_on: :class:`datetime.datetime` or ``None``
        :rtype: JSON dict
        :returns:
            success
                bool
            message
                Error message, if unsuccessful
            status_form
                Rendered XHTML for the status form, updated to reflect the
                changes made.

        """
        media = fetch_row(Media, id, incl_trash=True)

        # Make the requested change assuming it will be allowed
        if update_button == 'Review Complete':
            media.status.discard('unreviewed')
        elif update_button == 'Publish Now':
            media.status.discard('draft')
            media.status.add('publish')
            media.publish_on = publish_on or datetime.now()
        elif publish_on:
            media.publish_on = publish_on

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
