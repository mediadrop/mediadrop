# This file is a part of MediaCore, Copyright 2009 Simple Station Inc.
#
# MediaCore is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# MediaCore is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
Media Admin Controller
"""
import os.path
import re
import simplejson as json
import shutil
from urlparse import urlparse, urlunparse
from datetime import datetime

from tg import config, request, response, tmpl_context
from tg.controllers import CUSTOM_CONTENT_TYPE
from repoze.what.predicates import has_permission
from sqlalchemy import orm, sql
from formencode import validators
from paste.util import mimeparse
from PIL import Image

from mediacore.lib.base import (BaseController, url_for, redirect,
    expose, expose_xhr, validate, paginate)
from mediacore.model import (DBSession, fetch_row, get_available_slug,
    Media, MediaFile, Podcast, Tag, Author)
from mediacore.lib import helpers
from mediacore.model.media import create_media_stub
from mediacore.controllers.media import _add_new_media_file
from mediacore.forms.admin import SearchForm, ThumbForm
from mediacore.forms.media import (MediaForm, AddFileForm, EditFileForm,
    UpdateStatusForm, PodcastFilterForm)


media_form = MediaForm()
add_file_form = AddFileForm()
edit_file_form = EditFileForm()
thumb_form = ThumbForm()
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
        media = Media.query.options(orm.undefer('comment_count_published'))

        if search:
            media = media.admin_search(search)
        else:
            media = media.order_by_status()\
                         .order_by(Media.publish_on.desc(),
                                   Media.modified_on.desc())

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
            thumb_form
                The :class:`~mediacore.forms.admin.ThumbForm` instance
            thumb_action
                ``str`` form submit url
            update_status_form
                The :class:`~mediacore.forms.media.UpdateStatusForm` instance
            update_status_action
                ``str`` form submit url

        """
        media = fetch_row(Media, id)

        if tmpl_context.action == 'save' or id == 'new':
            # Use the values from error_handler or GET for new podcast media
            media_values = kwargs
            user = request.environ['repoze.who.identity']['user']
            media_values.setdefault('author_name', user.display_name)
            media_values.setdefault('author_email', user.email_address)
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
                details = dict(
                    duration = media.duration, # validator converts secs to hh:mm:ss
                ),
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
            thumb_form = thumb_form,
            thumb_action = url_for(action='save_thumb'),
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
        media = fetch_row(Media, id)

        if delete:
            DBSession.delete(media)
            DBSession.flush()
            redirect(action='index', id=None)

        media.slug = get_available_slug(Media, slug, media)
        media.title = title
        media.author = Author(author_name, author_email)
        media.description = helpers.clean_admin_xhtml(description)
        media.notes = notes
        media.duration = details['duration'] # validator converts hh:mm:ss to secs
        media.podcast_id = podcast
        media.set_tags(tags)
        media.set_topics(topics)

        media.update_status()
        DBSession.add(media)
        DBSession.flush()

        redirect(action='edit', id=media.id)


    @expose(content_type=CUSTOM_CONTENT_TYPE)
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
        :raises webob.exc.HTTPNotAcceptable: If the Accept header won't
            work with application/json or text/plain.

        .. note::

            This method returns incorrect Content-Type headers under
            some circumstances. It should be ``application/json``, but
            sometimes ``text/plain`` is used instead.

            This is because this method is used from the flash based
            uploader; Swiff.Uploader (which we use) uses Flash's
            FileReference.upload() method, which doesn't allow
            overriding the default HTTP headers.

            On windows, the default Accept header is "text/\*". This
            means that it won't accept "application/json". Rather than
            throw a 406 Not Acceptable response, or worse, a 500 error,
            we've chosen to return an incorrect ``text/plain`` type.

        """
        if id == 'new':
            media = create_media_stub()
        else:
            media = fetch_row(Media, id)

        try:
            if file is not None:
                # Create a media object, add it to the video, and store the file permanently.
                media_file = _add_new_media_file(media, file.filename, file.file)
            elif url:
                media_file = MediaFile()
                # Parse the URL checking for known embeddables like YouTube
                for type, info in config.embeddable_filetypes.iteritems():
                    match = info['pattern'].match(url)
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

            data = dict(
                success = True,
                media_id = media.id,
                file_id = media_file.id,
                edit_form = edit_form_xhtml,
                status_form = status_form_xhtml,
            )
        except Exception, e:
            data = dict(
                success = False,
                message = e.message,
            )

        response.headers['Content-Type'] = helpers.best_json_content_type()
        return json.dumps(data)

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
        media = fetch_row(Media, id)
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
        media = fetch_row(Media, id)
        data = {}

#        try:
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


    @expose(content_type=CUSTOM_CONTENT_TYPE)
    @validate(thumb_form, error_handler=edit)
    def save_thumb(self, id, thumb, **kwargs):
        """Save a thumbnail uploaded with :class:`~mediacore.forms.admin.ThumbForm`.

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
            media = fetch_row(Media, id)

        try:
            # Create thumbs
            img = Image.open(thumb.file)

            if id == 'new':
                DBSession.add(media)
                DBSession.flush()

            # TODO: Allow other formats?
            for key, xy in config.thumb_sizes[media._thumb_dir].iteritems():
                thumb_path = helpers.thumb_path(media, key)
                thumb_img = helpers.resize_thumb(img, xy)
                thumb_img.save(thumb_path)

            # Backup the original image just for kicks
            backup_type = os.path.splitext(thumb.filename)[1].lower()[1:]
            backup_path = helpers.thumb_path(media, 'orig', ext=backup_type)
            backup_file = open(backup_path, 'w+b')
            thumb.file.seek(0)
            shutil.copyfileobj(thumb.file, backup_file)
            thumb.file.close()
            backup_file.close()

            success = True
            message = None
        except IOError:
            success = False
            message = 'Unsupported image type'
        except Exception, e:
            success = False
            message = e.message

        response.headers['Content-Type'] = helpers.best_json_content_type()
        return json.dumps(dict(
            success = success,
            message = message,
            id = media.id,
        ))


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
        media = fetch_row(Media, id)

        # Make the requested change assuming it will be allowed
        if update_button == 'Review Complete':
            media.reviewed = True
        elif update_button == 'Publish Now':
            media.publishable = True
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
