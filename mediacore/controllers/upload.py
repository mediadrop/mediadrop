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
import os.path
import simplejson as json
import ftplib
import urllib2
import sha
import time
import logging
import formencode
from urlparse import urlparse
from datetime import datetime, timedelta, date

from akismet import Akismet
from formencode import validators
from paste.deploy.converters import asbool
from paste.util import mimeparse
from pylons import config, request, response, session, tmpl_context
from sqlalchemy import orm, sql

from mediacore.forms.uploader import UploadForm
from mediacore.lib import email
from mediacore.lib.base import BaseController
from mediacore.lib.decorators import expose, expose_xhr, paginate, validate
from mediacore.lib.helpers import (redirect, url_for, best_json_content_type,
	create_default_thumbs_for, fetch_setting)
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
                The :class:`~mediacore.forms.media.UploadForm` instance
            form_values
                ``dict`` form values, if any

        """
        support_emails = fetch_setting('email_support_requests')
        support_emails = email.parse_email_string(support_emails)
        support_email = support_emails and support_emails[0] or None

        return dict(
            legal_wording = fetch_setting('wording_user_uploads'),
            support_email = support_email,
            upload_form = upload_form,
            form_values = kwargs,
        )

    @expose()
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

        .. note::

            This method returns an incorrect Content-Type header under
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

        response.headers['Content-Type'] = best_json_content_type()
        return json.dumps(data)

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
        media_obj.notes = fetch_setting('wording_additional_notes')
        media_obj.set_tags(tags)

        # Create a media object, add it to the media_obj, and store the file permanently.
        if file is not None:
            media_file = _add_new_media_file(media_obj, file.filename, file.file)
        else:
            # FIXME: For some reason the media.type isn't ever set to video
            #        during this request. On subsequent requests, when
            #        media_obj.update_type() is called, it is set properly.
            #        This isn't too serious an issue right now because
            #        it is called the first time a moderator goes to review
            #        the new media_obj.
            media_file = MediaFile()
            url = unicode(url)
            for type, info in config['embeddable_filetypes'].iteritems():
                match = info['pattern'].match(url)
                if match:
                    media_file.type = type
                    media_file.url = match.group('id')
                    media_file.enable_feed = False
                    break
            else:
                # Trigger a validation error on the whole form.
                raise formencode.Invalid('Please specify a URL or upload a file below.', None, None)
            media_obj.files.append(media_file)

        # Add the final changes.
        media_obj.update_type()
        media_obj.update_status()
        DBSession.add(media_obj)
        DBSession.flush()

        create_default_thumbs_for(media_obj)

        return media_obj


# FIXME: The following helper methods should perhaps  be moved to the media controller.
#        or some other more generic place.
def _add_new_media_file(media, original_filename, file):
    # FIXME: I think this will raise a KeyError if the uploaded
    #        file doesn't have an extension.
    file_ext = os.path.splitext(original_filename)[1].lower()[1:]

    # set the file paths depending on the file type
    media_file = MediaFile()
    media_file.type = file_ext
    media_file.url = 'dummy_url' # model requires that url not NULL
    media_file.is_original = True
    media_file.enable_player = media_file.is_playable
    media_file.enable_feed = not media_file.is_embeddable
    media_file.size = os.fstat(file.fileno())[6]

    # update media relations
    media.files.append(media_file)

    # add the media file (and its media, if new) to the database to get IDs
    DBSession.add(media_file)
    DBSession.flush()

    # copy the file to its permanent location
    file_name = '%d_%d_%s.%s' % (media.id, media_file.id, media.slug, file_ext)
    file_url = _store_media_file(file, file_name)
    media_file.url = file_url

    return media_file

def _store_media_file(file, file_name):
    """Copy the file to its permanent location and return its URI"""
    if asbool(config['ftp_storage']):
        # Put the file into our FTP storage, return its URL
        return _store_media_file_ftp(file, file_name)
    else:
        # Store the file locally, return its path relative to the media dir
        file_path = os.path.join(config['media_dir'], file_name)
        permanent_file = open(file_path, 'w')
        shutil.copyfileobj(file, permanent_file)
        file.close()
        permanent_file.close()
        return file_name

class FTPUploadException(Exception):
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
    file_url = config['ftp_download_url'] + file_name

    # Put the file into our FTP storage
    FTPSession = ftplib.FTP(config['ftp_server'],
                            config['ftp_username'],
                            config['ftp_password'])

    try:
        FTPSession.cwd(config['ftp_upload_path'])
        FTPSession.storbinary(stor_cmd, file)
        _verify_ftp_upload_integrity(file, file_url)
    except Exception, e:
        FTPSession.quit()
        raise e

    FTPSession.quit()

    return file_url


def _verify_ftp_upload_integrity(file, file_url):
    """Download the file, and make sure that it matches the original.

    Returns True on success, and raises an Exception on failure.

    FIXME: Ideally we wouldn't have to download the whole file, we'd have
           some better way of verifying the integrity of the upload.
    """
    file.seek(0)
    old_hash = sha.new(file.read()).hexdigest()
    tries = 0

    # Try to download the file. Increase the number of retries, or the
    # timeout duration, if the server is particularly slow.
    # eg: Akamai usually takes 3-15 seconds to make an uploaded file
    #     available over HTTP.
    while tries < config['ftp_upload_integrity_retries']:
        time.sleep(3)
        tries += 1
        try:
            temp_file = urllib2.urlopen(file_url)
            new_hash = sha.new(temp_file.read()).hexdigest()
            temp_file.close()

            # If the downloaded file matches, success! Otherwise, we can
            # be pretty sure that it got corrupted during FTP transfer.
            if old_hash == new_hash:
                return True
            else:
                raise FTPUploadException(
                    'Uploaded File and Downloaded File did not match')
        except urllib2.HTTPError, e:
            pass

    raise FTPUploadException(
        'Could not download the file after %d attempts' % max)
