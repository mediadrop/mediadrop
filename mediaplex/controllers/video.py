"""
Video Controller

"""
import math
import shutil
import os.path
import simplejson as json
import time
import ftplib
import sha
import urllib2

from urlparse import urlparse, urlunparse
from cgi import parse_qs
from PIL import Image
from datetime import datetime
from tg import expose, validate, flash, require, url, request, response, config, tmpl_context
from tg.decorators import paginate
from tg.controllers import CUSTOM_CONTENT_TYPE
from tg.exceptions import HTTPNotFound
from formencode import validators
from pylons.i18n import ugettext as _
from sqlalchemy import and_, or_
from sqlalchemy.orm import eagerload, undefer
from sqlalchemy.orm.exc import NoResultFound

from mediaplex.lib import helpers, email
from mediaplex.lib.helpers import expose_xhr, redirect, url_for, clean_xhtml, strip_xhtml, line_break_xhtml
from mediaplex.lib.base import Controller, RoutingController
from mediaplex.model import DBSession, metadata, fetch_row, get_available_slug, Media, MediaFile, Comment, Tag, Topic, Author, AuthorWithIP
from mediaplex.forms.media import UploadForm
from mediaplex.forms.comments import PostCommentForm


upload_form = UploadForm(
    action = url_for(controller='/video', action='upload_submit'),
    async_action = url_for(controller='/video', action='upload_submit_async')
)

class FTPUploadException(Exception):
    pass


class VideoController(RoutingController):
    """Public video list actions"""

    def __init__(self, *args, **kwargs):
        super(VideoController, self).__init__(*args, **kwargs)
        tmpl_context.topics = DBSession.query(Topic)\
            .options(undefer('published_media_count'))\
            .filter(Topic.published_media_count >= 1)\
            .order_by(Topic.name)\
            .all()


    @expose('mediaplex.templates.video.index')
    @paginate('videos', items_per_page=20)
    def index(self, page=1, **kwargs):
        """Grid-style List Action"""
        return dict(
            videos = self._list_query.options(undefer('comment_count')),
        )


    @expose('mediaplex.templates.video.mediaflow')
    def flow(self, page=1, **kwargs):
        """Mediaflow Action"""
        return dict(
            videos = self._list_query[:15],
        )

    @expose('mediaplex.templates.video.concept_preview')
    def concept_preview(self, page=1, **kwargs):
        """Mediaflow Action"""
        tmpl_context.disable_topics = True
        tmpl_context.disable_sections = True

        try:
            topic = fetch_row(Topic, slug='conceptsundayschool')
            videos = self._list_query\
                    .filter(Media.topics.contains(topic))\
                    .order_by(Media.publish_on.desc())[:15]
        except HTTPNotFound, e:
            videos = []

        return dict(
            videos = videos
        )

    @property
    def _list_query(self):
        """Helper method for paginating video results"""
        return DBSession.query(Media)\
            .filter(Media.type == 'video')\
            .filter(Media.status >= 'publish')\
            .filter(Media.publish_on <= datetime.now())\
            .filter(Media.status.excludes('trash'))\
            .filter(Media.podcast_id == None)\
            .order_by(Media.publish_on.desc())


    @expose('mediaplex.templates.video.index')
    @paginate('videos', items_per_page=20)
    def topics(self, slug=None, page=1, **kwargs):
        if slug is None:
            redirect(action='index')
        topic = fetch_row(Topic, slug=slug)
        video_query = self._list_query\
            .filter(Media.topics.contains(topic))\
            .options(undefer('comment_count'))
        return dict(
            videos = video_query,
        )

    @expose('mediaplex.templates.video.index')
    @paginate('videos', items_per_page=20)
    def tags(self, slug=None, page=1, **kwargs):
        if slug is None:
            redirect(action='index')
        tag = fetch_row(Tag, slug=slug)
        video_query = self._list_query\
            .filter(Media.tags.contains(tag))\
            .options(undefer('comment_count'))
        return dict(
            videos = video_query,
        )

    @expose('mediaplex.templates.video.upload')
    def upload(self, **kwargs):
        return dict(
            upload_form = upload_form,
            form_values = {},
        )

    @expose('json')
    @validate(upload_form)
    def upload_submit_async(self, **kwargs):
        if 'validate' in kwargs:
            # we're just validating the fields. no need to worry.
            fields = json.loads(kwargs['validate'])
            err = {}
            for field in fields:
                if field in tmpl_context.form_errors:
                    err[field] = tmpl_context.form_errors[field]

            return dict(
                valid = len(err) == 0,
                err = err
            )
        else:
            # We're actually supposed to save the fields. Let's do it.
            if len(tmpl_context.form_errors) != 0:
                # if the form wasn't valid, return failure
                return dict(
                    success = False
                )

            # else actually save it!
            if 'name' not in kwargs:
                kwargs['name'] = None
            if 'tags' not in kwargs:
                kwargs['tags'] = None

            video = self._save_video(
                kwargs['name'], kwargs['email'],
                kwargs['title'], kwargs['description'],
                kwargs['tags'], kwargs['file']
            )
            email.send_video_notification(video)

            return dict(
                success = True,
                redirect = url_for(action='upload_success')
            )


    @expose()
    @validate(upload_form, error_handler=upload)
    def upload_submit(self, **kwargs):
        if 'name' not in kwargs:
            kwargs['name'] = None
        if 'tags' not in kwargs:
            kwargs['tags'] = None

        # Save the video!
        video = self._save_video(
            kwargs['name'], kwargs['email'],
            kwargs['title'], kwargs['description'],
            kwargs['tags'], kwargs['file']
        )
        email.send_video_notification(video)

        # Redirect to success page!
        redirect(action='upload_success')


    @expose('mediaplex.templates.video.upload-success')
    def upload_success(self, **kwargs):
        return dict()


    @expose('mediaplex.templates.video.upload-failure')
    def upload_failure(self, **kwargs):
        return dict()

    def _save_video(self, name, email, title, description, tags, file):
        # cope with anonymous posters
        if name is None:
            name = 'Anonymous'

        file_ext = os.path.splitext(file.filename)[1].lower()[1:]

        # create our video object as a status-less placeholder initially
        video = Media()
        video.type = 'video'
        video.author = Author(name, email)
        video.title = title
        video.slug = get_available_slug(Media, title)
        video.description = clean_xhtml(description)
        video.status = 'draft,unencoded,unreviewed'
        video.notes = """Bible References: None
S&H References: None
Reviewer: None
License: General Upload"""

        # set the file paths depending on the file type
        media_file = MediaFile()
        media_file.type = file_ext
        media_file.url = 'dummy_url' # model requires that url not NULL
        media_file.is_original = True
        media_file.enable_player = media_file.is_playable
        media_file.enable_feed = not media_file.is_embeddable
        media_file.size = os.fstat(file.file.fileno())[6]

        # update video relations
        video.files.append(media_file)

        # add the video (and its new media object) to the database to get IDs
        DBSession.add(video)
        DBSession.flush()

        # copy the file to its permanent location
        file_name = '%d_%d_%s.%s' % (video.id, media_file.id, video.slug, file_ext)
        file_url = self._store_video_file(file, file_name)
        media_file.url = file_url

        # If the file is a playable type, it doesn't need encoding
        # FIXME: is this a safe assumption? What about resolution/bitrate?
        if file_ext in config.playable_types['video']:
            video.status.discard('unencoded')

        video.set_tags(tags)

        # Add the final changes.
        DBSession.add(video)

        return video

    def _store_video_file(self, uploaded_file, file_name):
        """Copy the file to its permanent location and return its URI"""
        if config.ftp_storage:
            # Put the file into our FTP storage, return its URL
            return self._store_video_file_ftp(uploaded_file, file_name)
        else:
            # Store the file locally, return its path relative to the media dir
            file_path = os.path.join(config.media_dir, file_name)
            permanent_file = open(file_path, 'w')
            shutil.copyfileobj(uploaded_file.file, permanent_file)
            uploaded_file.file.close()
            permanent_file.close()
            return file_name

    def _store_video_file_ftp(self, uploaded_file, file_name):
        """Store the file on the defined FTP server.

        Returns the download url for accessing the resource.

        Ensures that the file was stored correctly and is accessible
        via the download url.

        Raises an exception on failure (FTP connection errors, I/O errors,
        integrity errors)
        """
        file = uploaded_file.file
        stor_cmd = 'STOR ' + file_name
        file_url = config.ftp_download_url + file_name

        # Put the file into our FTP storage
        FTPSession = ftplib.FTP(config.ftp_server, config.ftp_user, config.ftp_password)

        try:
            FTPSession.cwd(config.ftp_upload_directory)
            FTPSession.storbinary(stor_cmd, file)
            self._verify_ftp_upload_integrity(file, file_url)
        except Exception, e:
            FTPSession.quit()
            raise e

        FTPSession.quit()

        return file_url

    def _verify_ftp_upload_integrity(self, file, file_url):
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
        while tries < config.ftp_upload_integrity_retries:
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

