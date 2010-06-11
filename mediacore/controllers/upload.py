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

import shutil
import os
import simplejson as json
import ftplib
import urllib2
import time
import logging
import formencode
from urlparse import urlparse
from datetime import datetime, timedelta, date

from akismet import Akismet
from formencode import validators
from paste.deploy.converters import asbool
from paste.util import mimeparse
from pylons import app_globals, config, request, response, session, tmpl_context
from pylons.i18n import _
from sqlalchemy import orm, sql

from mediacore.forms.uploader import UploadForm
from mediacore.lib import email
from mediacore.lib.base import BaseController
from mediacore.lib.compat import sha1
from mediacore.lib.decorators import expose, expose_xhr, paginate, validate
from mediacore.lib.filetypes import guess_container_format, guess_media_type, parse_embed_url
from mediacore.lib.helpers import (accepted_extensions, redirect, url_for,
    create_default_thumbs_for)
from mediacore.model import (fetch_row, get_available_slug,
    Media, MediaFile, Comment, Tag, Category, Author, AuthorWithIP, Podcast)
from mediacore.model.meta import DBSession

import logging
log = logging.getLogger(__name__)

upload_form = UploadForm(
    action = url_for(controller='/upload', action='submit'),
    async_action = url_for(controller='/upload', action='submit_async')
)


class UploadController(BaseController):
    """
    Media Upload Controller
    """

    @expose('upload/index.html')
    def index(self, **kwargs):
        """Display the upload form.

        :rtype: Dict
        :returns:
            legal_wording
                XHTML legal wording for rendering
            support_email
                An help contact address
            upload_form
                The :class:`~mediacore.forms.uploader.UploadForm` instance
            form_values
                ``dict`` form values, if any

        """
        support_emails = app_globals.settings['email_support_requests']
        support_emails = email.parse_email_string(support_emails)
        support_email = support_emails and support_emails[0] or None

        return dict(
            legal_wording = app_globals.settings['wording_user_uploads'],
            support_email = support_email,
            upload_form = upload_form,
            form_values = kwargs,
        )

    @expose('json')
    @validate(upload_form)
    def submit_async(self, **kwargs):
        """Ajax form validation and/or submission.

        This is the save handler for :class:`~mediacore.forms.media.UploadForm`.

        When ajax is enabled this action is called for each field as the user
        fills them in. Although the entire form is validated, the JS only
        provides the value of one field at a time,

        :param validate: A JSON list of field names to check for validation
        :parma \*\*kwargs: One or more form field values.
        :rtype: JSON dict
        :returns:
            :When validating one or more fields:

            valid
                bool
            err
                A dict of error messages keyed by the field names

            :When saving an upload:

            success
                bool
            redirect
                If valid, the redirect url for the upload successful page.

        """
        if 'validate' in kwargs:
            # we're just validating the fields. no need to worry.
            fields = json.loads(kwargs['validate'])
            err = {}
            for field in fields:
                if field in tmpl_context.form_errors:
                    err[field] = tmpl_context.form_errors[field]

            data = dict(
                valid = len(err) == 0,
                err = err
            )
        else:
            # We're actually supposed to save the fields. Let's do it.
            if len(tmpl_context.form_errors) != 0:
                # if the form wasn't valid, return failure
                tmpl_context.form_errors['success'] = False
                data = tmpl_context.form_errors
            else:
                # else actually save it!
                kwargs.setdefault('name')
                kwargs.setdefault('tags')

                media_obj = self._save_media_obj(
                    kwargs['name'], kwargs['email'],
                    kwargs['title'], kwargs['description'],
                    kwargs['tags'], kwargs['file'], kwargs['url'],
                )
                email.send_media_notification(media_obj)
                data = dict(
                    success = True,
                    redirect = url_for(action='success')
                )

        return data

    @expose()
    @validate(upload_form, error_handler=index)
    def submit(self, **kwargs):
        """
        """
        kwargs.setdefault('name')
        kwargs.setdefault('tags')

        # Save the media_obj!
        media_obj = self._save_media_obj(
            kwargs['name'], kwargs['email'],
            kwargs['title'], kwargs['description'],
            kwargs['tags'], kwargs['file'], kwargs['url'],
        )
        email.send_media_notification(media_obj)

        # Redirect to success page!
        redirect(action='success')

    @expose('upload/success.html')
    def success(self, **kwargs):
        return dict()

    @expose('upload/failure.html')
    def failure(self, **kwargs):
        return dict()

    def _save_media_obj(self, name, email, title, description, tags, file, url):
        # create our media object as a status-less placeholder initially
        media_obj = Media()
        media_obj.author = Author(name, email)
        media_obj.title = title
        media_obj.slug = get_available_slug(Media, title)
        media_obj.description = description
        media_obj.notes = app_globals.settings['wording_additional_notes']
        media_obj.set_tags(tags)

        # Create a media object, add it to the media_obj, and store the file permanently.
        if file is not None:
            media_file = _add_new_media_file(media_obj, file.filename, file.file)
        else:
            media_file = MediaFile()
            url = unicode(url)
            embed = parse_embed_url(url)
            if embed:
                media_file.type = embed['type']
                media_file.container = embed['container']
                media_file.embed = embed['id']
                media_file.display_name = '%s ID: %s' % \
                    (embed['container'].capitalize(), media_file.embed)
            else:
                # Check for types we can play ourselves
                ext = os.path.splitext(url)[1].lower()[1:]
                container = guess_container_format(ext)
                if container in accepted_extensions():
                    media_file.type = guess_media_type(container)
                    media_file.container = container
                    media_file.url = url
                    media_file.display_name = os.path.basename(url)
                else:
                    # Trigger a validation error on the whole form.
                    raise formencode.Invalid(_('Please specify a URL or upload a file below.'), None, None)
            media_obj.files.append(media_file)

        # Add the final changes.
        media_obj.update_status()
        DBSession.add(media_obj)
        DBSession.flush()

        create_default_thumbs_for(media_obj)

        return media_obj


# FIXME: The following helper methods should perhaps  be moved to the media controller.
#        or some other more generic place.
def _add_new_media_file(media, original_filename, file):
    file_ext = os.path.splitext(original_filename)[1].lower().lstrip('.')
    container = guess_container_format(file_ext)

    if container is None:
        msg = _('File extension "%s" is not supported.') % file_ext
        raise formencode.Invalid(msg, file_ext, None)

    # set the file paths depending on the file type
    media_file = MediaFile()
    media_file.display_name = original_filename
    media_file.container = guess_container_format(file_ext)
    media_file.type = guess_media_type(media_file.container)

    # Small files are stored in memory and do not have a tmp file w/ fileno
    if hasattr(file, 'fileno'):
        media_file.size = os.fstat(file.fileno())[6]
    else:
        # The file may contain multi-byte characters, so we must seek instead of count chars
        file.seek(0, os.SEEK_END)
        media_file.size = file.tell()
        file.seek(0)

    # update media relations
    media.files.append(media_file)

    # add the media file (and its media, if new) to the database to get IDs
    DBSession.add(media_file)
    DBSession.flush()

    # copy the file to its permanent location
    file_name = '%d_%d_%s.%s' % (media.id, media_file.id, media.slug, file_ext)
    file_url = _store_media_file(file, file_name)

    if file_url:
        # The file has been stored remotely
        media_file.url = file_url
    else:
        # The file is stored locally and we just need its name
        media_file.file_name = file_name

    return media_file

def _store_media_file(file, file_name):
    """Copy the file to its permanent location and return its URI"""
    if asbool(app_globals.settings['ftp_storage']):
        # Put the file into our FTP storage, return its URL
        return _store_media_file_ftp(file, file_name)
    else:
        # Store the file locally, return its path relative to the media dir
        file_path = os.path.join(config['media_dir'], file_name)
        file.seek(0)
        permanent_file = open(file_path, 'w')
        shutil.copyfileobj(file, permanent_file)
        file.close()
        permanent_file.close()
        return None # The file name is unchanged, so return nothing

class FTPUploadException(formencode.Invalid):
    pass

def _store_media_file_ftp(file, file_name):
    """Store the file on the defined FTP server.

    Returns the download url for accessing the resource.

    Ensures that the file was stored correctly and is accessible
    via the download url.

    Raises an exception on failure (FTP connection errors, I/O errors,
    integrity errors)
    """
    stor_cmd = 'STOR ' + file_name
    file_url = app_globals.settings['ftp_download_url'].rstrip('/') + '/' + file_name
    ftp_server = app_globals.settings['ftp_server']
    ftp_user = app_globals.settings['ftp_user']
    ftp_password = app_globals.settings['ftp_password']
    upload_dir = app_globals.settings['ftp_upload_directory']

    # Put the file into our FTP storage
    FTPSession = ftplib.FTP(ftp_server, ftp_user, ftp_password)

    try:
        if upload_dir:
            FTPSession.cwd(upload_dir)
        FTPSession.storbinary(stor_cmd, file)
        _verify_ftp_upload_integrity(file, file_url)
        # TODO: Delete the file if the integrity check fails
    finally:
        FTPSession.quit()

    return file_url

def _verify_ftp_upload_integrity(file, file_url):
    """Download the file and make sure that it matches the original.

    Returns True on success, and raises a formencode.Invalid on failure
    so that the error may be displayed to the user.

    FIXME: Ideally we wouldn't have to download the whole file, we'd have
           some better way of verifying the integrity of the upload.

    """
    tries = 0
    max_tries = int(app_globals.settings['ftp_upload_integrity_retries'])
    if max_tries < 1:
        return True

    file.seek(0)
    orig_hash = sha1(file.read()).hexdigest()

    # Try to download the file. Increase the number of retries, or the
    # timeout duration, if the server is particularly slow.
    # eg: Akamai usually takes 3-15 seconds to make an uploaded file
    #     available over HTTP.
    while tries < max_tries:
        tries += 1
        try:
            temp_file = urllib2.urlopen(file_url)
            new_hash = sha1(temp_file.read()).hexdigest()
            temp_file.close()

            # If the downloaded file matches, success! Otherwise, we can
            # be pretty sure that it got corrupted during FTP transfer.
            if orig_hash == new_hash:
                return True
            else:
                msg = _('The file transferred to your FTP server is '\
                        'corrupted. Please try again.')
                raise FTPUploadException(msg, None, None)
        except urllib2.HTTPError, http_err:
            # Don't raise the exception now, wait until all attempts fail
            time.sleep(3)

    # Raise the exception from the last attempt
    msg = _('Could not download the file from your FTP server: %s')\
        % http_err.message
    raise FTPUploadException(msg, None, None)
