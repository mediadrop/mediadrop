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
import shutil
from datetime import datetime
from urlparse import urlparse, urlunparse

from formencode import validators
from paste.util import mimeparse
from pylons import config, request, response, session, tmpl_context
from pylons.i18n import _
from repoze.what.predicates import has_permission
from sqlalchemy import orm, sql

from mediacore.controllers.upload import _generic_add_new_media_file
from mediacore.forms.admin import SearchForm, ThumbForm
from mediacore.forms.admin.media import AddFileForm, EditFileForm, MediaForm, PodcastFilterForm, UpdateStatusForm
from mediacore.lib import helpers
from mediacore.lib.base import BaseController
from mediacore.lib.decorators import expose, expose_xhr, paginate, validate
from mediacore.lib.filetypes import guess_container_format, guess_media_type, parse_embed_url
from mediacore.lib.helpers import redirect, url_for
from mediacore.model import Author, Category, Media, Podcast, Tag, fetch_row, get_available_slug
from mediacore.model.meta import DBSession

import logging
log = logging.getLogger(__name__)

media_form = MediaForm()
add_file_form = AddFileForm()
edit_file_form = EditFileForm()
thumb_form = ThumbForm()
update_status_form = UpdateStatusForm()
search_form = SearchForm(action=url_for(controller='/admin/media', action='index'))
podcast_filter_form = PodcastFilterForm(action=url_for(controller='/admin/media', action='index'))

class MediaController(BaseController):
    allow_only = has_permission('admin')

    @expose_xhr('admin/media/index.html', 'admin/media/index-table.html')
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
                The :class:`~mediacore.forms.admin.media.PodcastFilterForm` instance.

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


    @expose('admin/media/edit.html')
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
                The :class:`~mediacore.forms.admin.media.MediaForm` instance
            media_action
                ``str`` form submit url
            media_values
                ``dict`` form values
            file_add_form
                The :class:`~mediacore.forms.admin.media.AddFileForm` instance
            file_add_action
                ``str`` form submit url
            file_edit_form
                The :class:`~mediacore.forms.admin.media.EditFileForm` instance
            file_edit_action
                ``str`` form submit url
            thumb_form
                The :class:`~mediacore.forms.admin.ThumbForm` instance
            thumb_action
                ``str`` form submit url
            update_status_form
                The :class:`~mediacore.forms.admin.media.UpdateStatusForm` instance
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
                categories = [category.id for category in media.categories],
                notes = media.notes,
            )

        # Re-verify the state of our Media object in case the data is nonsensical
        if id != 'new':
            media.update_status()
            DBSession.add(media)

        return dict(
            media = media,
            media_form = media_form,
            media_action = url_for(action='save'),
            media_values = media_values,
            category_tree = Category.query.order_by(Category.name).populated_tree(),
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
             description, notes, podcast, tags, categories,
             delete=None, **kwargs):
        """Save changes or create a new :class:`~mediacore.model.media.Media` instance.

        Form handler the :meth:`edit` action and the
        :class:`~mediacore.forms.admin.media.MediaForm`.

        Redirects back to :meth:`edit` after successful editing
        and :meth:`index` after successful deletion.

        """
        media = fetch_row(Media, id)

        if delete:
            file_paths = helpers.thumb_paths(media)
            for f in media.files:
                file_paths.append(f.file_path)
                # Remove the file from the session so that SQLAlchemy doesn't
                # try to issue an UPDATE to set the MediaFile.media_id to None.
                # The database ON DELETE CASCADE handles everything for us.
                DBSession.expunge(f)
            DBSession.delete(media)
            DBSession.commit()
            helpers.delete_files(file_paths, 'media')
            redirect(action='index', id=None)

        media.slug = get_available_slug(Media, slug, media)
        media.title = title
        media.author = Author(author_name, author_email)
        media.description = description
        media.notes = notes
        media.podcast_id = podcast
        media.set_tags(tags)
        media.set_categories(categories)

        media.update_status()
        DBSession.add(media)
        DBSession.flush()

        if id == 'new':
            helpers.create_default_thumbs_for(media)

        redirect(action='edit', id=media.id)


    @expose('json')
    @validate(add_file_form)
    def add_file(self, id, file=None, url=None, **kwargs):
        """Save action for the :class:`~mediacore.forms.admin.media.AddFileForm`.

        Creates a new :class:`~mediacore.model.media.MediaFile` from the
        uploaded file or the local or remote URL.

        :param id: Media ID. If ``"new"`` a new Media stub is created.
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
                The rendered XHTML :class:`~mediacore.forms.admin.media.EditFileForm`
                for this file.
            status_form
                The rendered XHTML :class:`~mediacore.forms.admin.media.UpdateStatusForm`

        """
        if id == 'new':
            media = Media()
            user = request.environ['repoze.who.identity']['user']
            media.author = Author(user.display_name, user.email_address)
            # Create a temp stub until we can set it to something meaningful
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            media.title = u'Temporary stub %s' % timestamp
            media.slug = get_available_slug(Media, '_slug_' + timestamp)
        else:
            media = fetch_row(Media, id)

        if file is not None:
            media_file, message = _generic_add_new_media_file(media, file.filename, file.file)
        elif url:
            media_file, message = _generic_add_new_media_file(media, url)
        else:
            message = _('No action to perform.')

        if not message:
            data = {'success': True}
            media.update_status()

            if id == 'new':
                media.title = media_file.display_name
                media.slug = get_available_slug(Media, '_stub_' + media.title)
                helpers.create_default_thumbs_for(media)

            # Render some widgets so the XHTML can be injected into the page
            edit_form_xhtml = unicode(edit_file_form.display(
                action=url_for(action='edit_file', id=media.id),
                file=media_file))
            status_form_xhtml = unicode(update_status_form.display(
                action=url_for(action='update_status', id=media.id),
                media=media))

            data.update(dict(
                media_id = media.id,
                file_id = media_file.id,
                file_type = media_file.type,
                edit_form = edit_form_xhtml,
                status_form = status_form_xhtml,
            ))
        else:
            data = {'success': False, 'message': message}

        return data


    @expose('json')
    @validate(validators={'file_id': validators.Int()})
    def edit_file(self, id, file_id, file_type=None, duration=None, delete=None, **kwargs):
        """Save action for the :class:`~mediacore.forms.admin.media.EditFileForm`.

        Changes or delets a :class:`~mediacore.model.media.MediaFile`.

        TODO: Use the form validators to validate this form. We only
              POST one field at a time, so the validate decorator doesn't
              work, because it doesn't work for partial validation, because
              none of the kwargs are updated if an Invalid exception is
              raised by any validator.

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
        data = dict(success=False)

        try:
            file = [file for file in media.files if file.id == file_id][0]
        except IndexError:
            file = None

        if file is None:
            data['message'] = _('File "%s" does not exist.') % file_id
        elif file_type:
            file.type = file_type
            DBSession.add(file)
            data['success'] = True
        elif duration is not None:
            try:
                duration = helpers.duration_to_seconds(duration)
            except ValueError:
                data['message'] = _('Bad duration formatting, use Hour:Min:Sec')
            else:
                media.duration = duration
                DBSession.add(media)
                data['success'] = True
                data['duration'] = helpers.duration_from_seconds(duration)
        elif delete:
            file_path = file.file_path
            DBSession.delete(file)
            DBSession.commit()
            if file_path:
                helpers.delete_files([file_path], 'media')
            media = fetch_row(Media, id)
            data['success'] = True
        else:
            data['message'] = _('No action to perform.')

        if data['success']:
            data['file_type'] = file.type
            media.update_status()
            DBSession.add(media)
            DBSession.flush()

            # Return the rendered widget for injection
            status_form_xhtml = unicode(update_status_form.display(
                action=url_for(action='update_status'), media=media))
            data['status_form'] = status_form_xhtml
        return data


    @expose('json')
    @validate(thumb_form, error_handler=edit)
    def save_thumb(self, id, thumb, **kwargs):
        """Save a thumbnail uploaded with :class:`~mediacore.forms.admin.ThumbForm`.

        :param id: Media ID. If ``"new"`` a new Media stub is created.
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
            media = Media()
            user = request.environ['repoze.who.identity']['user']
            media.author = Author(user.display_name, user.email_address)
            media.title = os.path.basename(thumb.filename)
            media.slug = get_available_slug(Media, '_stub_' + media.title)
            DBSession.add(media)
            DBSession.flush()
        else:
            media = fetch_row(Media, id)

        try:
            # Create JPEG thumbs
            helpers.create_thumbs_for(media, thumb.file, thumb.filename)
            success = True
            message = None
        except IOError:
            success = False
            message = _('Unsupported image type')
        except Exception, e:
            success = False
            message = e.message

        if message is not None and id == 'new':
            DBSession.delete(media)

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
        media = fetch_row(Media, id)

        # Make the requested change assuming it will be allowed
        if update_button == _('Review Complete'):
            media.reviewed = True
        elif update_button == _('Publish Now'):
            media.publishable = True
            media.publish_on = publish_on or datetime.now()
            media.update_popularity()
        elif publish_on:
            media.publish_on = publish_on
            media.update_popularity()

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
