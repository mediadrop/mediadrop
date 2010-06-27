import formencode
import ftplib
import os
import time
import urllib2

from paste.deploy.converters import asbool
from pylons import config
from pylons.i18n import _

from mediacore.lib.compat import sha1
from mediacore.lib.filetypes import (guess_container_format, guess_media_type,
    parse_embed_url)
from mediacore.lib.helpers import create_default_thumbs_for
from mediacore.model import Author, Media, MediaFile, get_available_slug
from mediacore.model.meta import DBSession

import logging
log = logging.getLogger(__name__)

__all__ = [
    'add_new_media_file',
    'save_media_obj',
    'FTPUploadException',
]

class FTPUploadException(formencode.Invalid):
    pass

def add_new_media_file(media, uploaded_file=None, url=None):
    """Create a new MediaFile for the provided Media object and File/URL
    and add it to that Media object's files list.

    :param media: The Media object to append the file to
    :type media: :class:`~mediacore.model.media.Media` instance
    :param uploaded_file: An object with 'filename' and 'file' properties.
    :type uploaded_file: Formencode uploaded file object.
    :param url: The URL to represent, if no file is given.
    :type url: unicode
    :returns: The created MediaFile (or None)
    """
    if uploaded_file is not None:
        # Create a MediaFile object, add it to the video, and store the file permanently.
        media_file = media_file_from_filename(uploaded_file.filename)
        attach_and_store_media_file(media, media_file, uploaded_file.file)
    elif url is not None:
        # Looks like we were just given a URL. Create a MediaFile object with that URL.
        media_file = media_file_from_url(url)
        media.files.append(media_file)
    else:
        raise formencode.Invalid(_('No File or URL provided.'), None, None)

    media.update_status()
    DBSession.flush()

    return media_file

def base_ext_container_from_uri(uri):
    """Returns a 3-tuple of strings:

    - Base of the filename (without extension)
    - Normalized file extension (without preceding dot)
    - Best-guess container format.

    Raises a formencode.Invalid exception if a useful container isn't found.
    """
    name, file_ext = os.path.splitext(uri)
    ext = file_ext[1:].lower()
    container = guess_container_format(ext)
    if container is None:
        error_msg = _('File extension "%s" is not supported.') % file_ext
        raise formencode.Invalid(error_msg, None, None)
    return name, ext, container

def media_file_from_url(url):
    """Create and return  a MediaFile object representing a given URL.

    Does not add the created MediaFile to the database.
    """
    media_file = MediaFile()
    # Parse the URL checking for known embeddables like YouTube
    embed = parse_embed_url(url)
    if embed:
        media_file.type = embed['type']
        media_file.container = embed['container']
        media_file.embed = embed['id']
        media_file.display_name = '%s ID: %s' % \
            (embed['container'].capitalize(), media_file.embed)
    else:
        # Check for types we can play ourselves
        name, ext, container = base_ext_container_from_uri(url)
        media_file.type = guess_media_type(ext)
        media_file.container = container
        media_file.url = url
        media_file.display_name = os.path.basename(url)

    return media_file

def media_file_from_filename(filename):
    """Create and return a MediaFile object representing a given filename.

    Does not store the file, or add the created MediaFile to the database.
    """
    name, ext, container = base_ext_container_from_uri(filename)

    # set the file paths depending on the file type
    media_file = MediaFile()
    media_file.display_name = '%s.%s' % (name, container)
    media_file.container = container
    media_file.type = guess_media_type(ext)

    # File has not been stored. It has neither URL nor Filename.
    media_file.url = None
    media_file.file_name = None

    if file_url:
        # The file has been stored remotely
        media_file.url = file_url
    else:
        # The file is stored locally and we just need its name
        media_file.file_name = file_name

    return media_file

def attach_and_store_media_file(media, media_file, file):
    """Given a Media object, a MediaFile object, and a file handle,
    attaches the MediaFile to the Media object, and saves the file to permanent
    storage.

    Adds the MediaFile to the database.
    """
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
    file_name = '%d_%d_%s.%s' % (media.id, media_file.id, media.slug, media_file.container)
    file_url = store_media_file(file, file_name)

    if file_url:
        # The file has been stored remotely
        media_file.url = file_url
    else:
        # The file is stored locally and we just need its name
        media_file.file_name = file_name

def store_media_file(file, file_name):
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

def save_media_obj(name, email, title, description, tags, uploaded_file, url):
    # create our media object as a status-less placeholder initially
    media_obj = Media()
    media_obj.author = Author(name, email)
    media_obj.title = title
    media_obj.slug = get_available_slug(Media, title)
    media_obj.description = description
    media_obj.notes = app_globals.settings['wording_additional_notes']
    media_obj.set_tags(tags)

    # Give the Media object an ID.
    DBSession.add(media_obj)
    DBSession.flush()

    # Create a MediaFile object, add it to the media_obj, and store the file permanently.
    media_file = add_new_media_file(media_obj, uploaded_file, url)

    # Create the thumbnails
    create_default_thumbs_for(media_obj)

    return media_obj
