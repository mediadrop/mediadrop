import math
import shutil
import os.path
import simplejson as json
import time
import ftplib
import urllib2
import sha

from urlparse import urlparse
from cgi import parse_qs
from PIL import Image
from datetime import datetime, timedelta, date
from tg import expose, validate, flash, require, url, request, response, config, tmpl_context
from tg.exceptions import HTTPNotFound
from tg.decorators import paginate
from tg.controllers import CUSTOM_CONTENT_TYPE
from formencode import validators
from pylons.i18n import ugettext as _
from sqlalchemy import and_, or_, sql
from sqlalchemy.orm import eagerload, undefer
from sqlalchemy.orm.exc import NoResultFound

from simpleplex.lib import helpers, email
from simpleplex.lib.helpers import expose_xhr, redirect, url_for, clean_xhtml, strip_xhtml, line_break_xhtml
from simpleplex.lib.base import Controller, RoutingController
from simpleplex.model import DBSession, metadata, fetch_row, get_available_slug, Media, MediaFile, Comment, Tag, Topic, Author, AuthorWithIP, Podcast
from simpleplex.forms.media import UploadForm
from simpleplex.forms.comments import PostCommentForm

upload_form = UploadForm(
    action = url_for(controller='/media', action='upload_submit'),
    async_action = url_for(controller='/media', action='upload_submit_async')
)

post_comment_form = PostCommentForm()

class FTPUploadException(Exception):
    pass


class MediaController(RoutingController):
    """Media actions -- for both regular and podcast media"""

    def __init__(self, *args, **kwargs):
        super(MediaController, self).__init__(*args, **kwargs)
        tmpl_context.topics = DBSession.query(Topic)\
            .options(undefer('published_media_count'))\
            .having(sql.text('published_media_count >= 1'))\
            .order_by(Topic.name)\
            .all()

    @expose('simpleplex.templates.media.index')
    @paginate('media', items_per_page=20)
    def index(self, page=1, topics=None, **kwargs):
        """Grid-style List Action"""
        return dict(
            media = self._list_query.options(undefer('comment_count')),
        )

    @expose('simpleplex.templates.media.lessons')
    @paginate('media', items_per_page=20)
    def lessons(self, page=1, topics=None, **kwargs):
        """Grid-style List Action"""
        try:
            topic = fetch_row(Topic, slug='bible-lesson')
            media = DBSession.query(Media)\
                .filter(Media.topics.contains(topic))\
                .filter(Media.status >= 'publish')\
                .filter(Media.publish_on <= datetime.now())\
                .filter(Media.status.excludes('trash'))\
                .filter(Media.podcast_id == None)\
                .order_by(Media.publish_on.desc())\
                .options(undefer('comment_count_published'))
        except HTTPNotFound:
            media = []

        today = date.today()
        sunday = today - timedelta(days=today.weekday()+1)
        sunday = datetime(sunday.year, sunday.month, sunday.day)

        return dict(
            media = media,
            week_start = sunday,
        )

    @expose('simpleplex.templates.media.lesson_view')
    def lesson_view(self, slug, **kwargs):
        """Display the media player and comments"""
        media = fetch_row(Media, slug=slug)
        next_episode = None
        media.views += 1

        return dict(
            media = media,
            comment_form = PostCommentForm(action=url_for(action='lesson_comment')),
            comment_form_action = url_for(action='comment'),
            comment_form_values = kwargs,
            next_episode = next_episode,
        )

    @expose()
    @validate(PostCommentForm(), error_handler=lesson_view)
    def lesson_comment(self, slug, **values):
        media = fetch_row(Media, slug=slug)
        c = Comment()
        c.status = 'unreviewed'
        c.author = AuthorWithIP(values['name'], None, request.environ['REMOTE_ADDR'])
        c.subject = 'Re: %s' % media.title
        c.body = clean_xhtml(values['body'])

        media.comments.append(c)
        DBSession.add(media)
        email.send_comment_notification(media, c)
        redirect(action='lesson_view')

    @expose('simpleplex.templates.media.view')
    def view(self, slug, podcast_slug=None, **kwargs):
        """Display the media player and comments"""
        media = fetch_row(Media, slug=slug)
        media.views += 1

        next_episode = None
        if media.podcast_id is not None:
            # Always view podcast media from a URL that shows the context of the podcast
            if url_for() != url_for(podcast_slug=media.podcast.slug):
               redirect(podcast_slug=media.podcast.slug)

            if media.is_published:
                next_episode = DBSession.query(Media)\
                    .filter(Media.podcast_id == media.podcast.id)\
                    .filter(Media.publish_on > media.publish_on)\
                    .filter(Media.publish_on < datetime.now())\
                    .filter(Media.status >= 'publish')\
                    .filter(Media.status.excludes('trash'))\
                    .order_by(Media.publish_on)\
                    .first()

        return dict(
            media = media,
            comment_form = post_comment_form,
            comment_form_action = url_for(action='comment'),
            comment_form_values = kwargs,
            next_episode = next_episode,
        )

    @expose('json')
    def latest(self, **kwargs):
        """
        EXPOSE the basic properties of the latest media object
        TODO: work this into a more general, documented, API scheme

        Arguments:
            podcast - a podcast slug or empty string
            topic     - a topic slug
        """
        media_query = DBSession.query(Media)\
            .filter(Media.publish_on < datetime.now())\
            .filter(Media.status >= 'publish')\
            .filter(Media.status.excludes('trash'))

        # Filter by podcast, if podcast slug provided
        slug = kwargs.get('podcast', None)
        if slug != None:
            if slug != '':
                podcast = fetch_row(Podcast, slug=slug)
                media_query = media_query\
                    .filter(Media.podcast_id == podcast.id)
            else:
                media_query = media_query\
                    .filter(Media.podcast_id == None)

        # Filter by topic, if topic slug provided
        slug = kwargs.get('topic', None)
        if slug:
            topic = fetch_row(Topic, slug=slug)
            media_query = media_query\
                .filter(Media.topics.contains(topic))\

        # get the actual object (hope there is one!)
        media = media_query\
            .order_by(Media.publish_on.desc())\
            .first()

        return self._jsonify(media)

    @expose('json')
    def most_popular(self, **kwargs):
        """
        EXPOSE the basic properties of the most popular media object
        TODO: work this into a more general, documented, API scheme
        """
        media_query = DBSession.query(Media)\
            .filter(Media.publish_on < datetime.now())\
            .filter(Media.status >= 'publish')\
            .filter(Media.status.excludes('trash'))

        media = media_query.order_by(Media.views.desc()).first()
        return self._jsonify(media)

    def _jsonify(self, media):
        im_path = '/images/media/%d%%s.jpg' % media.id

        return dict(
            title = media.title,
            description = media.description,
            description_plain = strip_xhtml(line_break_xhtml(\
                line_break_xhtml(media.description))),
            img_l = url_for(im_path % 'l'),
            img_m = url_for(im_path % 'm'),
            img_s = url_for(im_path % 's'),
            img_ss = url_for(im_path % 'ss'),
            id = media.id,
            url = url_for(controller="/media", action="view", slug=media.slug),
            podcast = media.podcast and media.podcast.slug or None,
        )

    @expose('simpleplex.templates.media.concept_view')
    def concept_view(self, slug, podcast_slug=None, **kwargs):
        """Display the media player and comments"""
        media = fetch_row(Media, slug=slug)
        media.views += 1

        return dict(
            media = media,
            comment_form = PostCommentForm(action=url_for(action='concept_comment')),
            comment_form_action = url_for(action='comment'),
            comment_form_values = kwargs,
        )

    @expose()
    @validate(PostCommentForm(), error_handler=concept_view)
    def concept_comment(self, slug, **values):
        media = fetch_row(Media, slug=slug)
        c = Comment()
        c.status = 'unreviewed'
        c.author = AuthorWithIP(values['name'], None, request.environ['REMOTE_ADDR'])
        c.subject = 'Re: %s' % media.title
        c.body = clean_xhtml(values['body'])

        media.comments.append(c)
        DBSession.add(media)
        email.send_comment_notification(media, c)
        redirect(action='concept_view')


    @expose_xhr()
    @validate(validators=dict(rating=validators.Int()))
    def rate(self, slug, rating=1, **kwargs):
        media = fetch_row(Media, slug=slug)

        if rating > 0:
            media.rating.add_vote(1)
        else:
            media.rating.add_vote(0)
        DBSession.add(media)

        if request.is_xhr:
            return dict(
                success = True,
                upRating = helpers.text.plural(media.rating.sum, 'person', 'people'),
                downRating = None,
            )
        else:
            redirect(action='view')


    @expose()
    @validate(post_comment_form, error_handler=view)
    def comment(self, slug, **values):
        media = fetch_row(Media, slug=slug)
        c = Comment()
        c.status = 'unreviewed'
        c.author = AuthorWithIP(values['name'], None, request.environ['REMOTE_ADDR'])
        c.subject = 'Re: %s' % media.title
        c.body = clean_xhtml(values['body'])

        media.comments.append(c)
        DBSession.add(media)
        email.send_comment_notification(media, c)
        redirect(action='view')


    @expose()
    @validate(validators={'id': validators.Int()})
    def serve(self, id, slug, type, **kwargs):
        media = fetch_row(Media, slug=slug)

        for file in media.files:
            if file.id == id and file.type == type:
                # Redirect to an external URL
                if urlparse(file.url)[1]:
                    redirect(file.url.encode('utf-8'))
                file_path = os.path.join(config.media_dir, file.url)
                file_handle = open(file_path, 'rb')
                response.content_type = file.mimetype
                return file_handle.read()
        else:
            raise HTTPNotFound()

    @expose('simpleplex.templates.media.mediaflow')
    def flow(self, page=1, **kwargs):
        """Mediaflow Action"""
        return dict(
            media = self._list_query[:15],
        )

    @expose('simpleplex.templates.media.concept_preview')
    def concept_preview(self, page=1, **kwargs):
        """Mediaflow Action"""
        tmpl_context.disable_topics = True
        tmpl_context.disable_sections = True

        try:
            topic = fetch_row(Topic, slug='conceptsundayschool')
            media = self._published_media_query\
                    .filter(Media.topics.contains(topic))\
                    .order_by(Media.publish_on.desc())[:15]
        except HTTPNotFound, e:
            media = []

        return dict(
            media = media
        )

    @property
    def _list_query(self):
        """Helper method for paginating published media

        Filters out podcast media.
        """
        return self._published_media_query\
            .filter(Media.podcast_id == None)

    @property
    def _published_media_query(self):
        """Helper method for getting published media"""
        return DBSession.query(Media)\
            .filter(Media.status >= 'publish')\
            .filter(Media.publish_on <= datetime.now())\
            .filter(Media.status.excludes('trash'))\
            .order_by(Media.publish_on.desc())


    @expose('simpleplex.templates.media.topics')
    @paginate('media', items_per_page=20)
    def topics(self, slug=None, page=1, **kwargs):
        if slug:
            topic = fetch_row(Topic, slug=slug)
            media_query = self._published_media_query\
                .filter(Media.topics.contains(topic))\
                .options(undefer('comment_count_published'))
            media = media_query
        else:
            topic = None
            media = []

        return dict(
            media = media,
            topic = topic,
        )

    @expose('simpleplex.templates.media.tags')
    @paginate('media', items_per_page=20)
    def tags(self, slug=None, page=1, **kwargs):
        if slug:
            tag = fetch_row(Tag, slug=slug)
            media_query = self._published_media_query\
                .filter(Media.tags.contains(tag))\
                .options(undefer('comment_count_published'))
            media = media_query
            tags = None
        else:
            tag = None
            media = []
            tags = DBSession.query(Tag)\
                .options(undefer('published_media_count'))\
                .having(sql.text('published_media_count >= 1'))\
                .order_by(Tag.name)\
                .all()

        return dict(
            media = media,
            tag = tag,
            tags = tags,
        )

    @expose('simpleplex.templates.media.upload')
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

            media_obj = self._save_media_obj(
                kwargs['name'], kwargs['email'],
                kwargs['title'], kwargs['description'],
                kwargs['tags'], kwargs['file']
            )
            email.send_media_notification(media_obj)

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

        # Save the media_obj!
        media_obj = self._save_media_obj(
            kwargs['name'], kwargs['email'],
            kwargs['title'], kwargs['description'],
            kwargs['tags'], kwargs['file']
        )
        email.send_media_notification(media_obj)

        # Redirect to success page!
        redirect(action='upload_success')


    @expose('simpleplex.templates.media.upload-success')
    def upload_success(self, **kwargs):
        return dict()


    @expose('simpleplex.templates.media.upload-failure')
    def upload_failure(self, **kwargs):
        return dict()

    def _save_media_obj(self, name, email, title, description, tags, file):
        # cope with anonymous posters
        if name is None:
            name = 'Anonymous'

        # create our media object as a status-less placeholder initially
        media_obj = Media()
        media_obj.author = Author(name, email)
        media_obj.title = title
        media_obj.slug = get_available_slug(Media, title)
        media_obj.description = clean_xhtml(description)
        media_obj.status = 'draft,unencoded,unreviewed'
        media_obj.notes = (
            "Bible References: None\n"
            "S&H References: None\n"
            "Reviewer: None\n"
            "License: General Upload\n"
        )
        media_obj.set_tags(tags)

        # Create a media object, add it to the media_obj, and store the file permanently.
        media_file = _add_new_media_file(media_obj, file.filename, file.file)

        # If the file is a playable type, it doesn't need encoding
        # FIXME: is this a safe assumption? What about resolution/bitrate?
        if media_file.is_playable:
            media_obj.status.discard('unencoded')

        # Add the final changes.
        DBSession.add(media_obj)

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
    if config.ftp_storage:
        # Put the file into our FTP storage, return its URL
        return _store_media_file_ftp(file, file_name)
    else:
        # Store the file locally, return its path relative to the media dir
        file_path = os.path.join(config.media_dir, file_name)
        permanent_file = open(file_path, 'w')
        shutil.copyfileobj(file, permanent_file)
        file.close()
        permanent_file.close()
        return file_name

def _store_media_file_ftp(file, file_name):
    """Store the file on the defined FTP server.

    Returns the download url for accessing the resource.

    Ensures that the file was stored correctly and is accessible
    via the download url.

    Raises an exception on failure (FTP connection errors, I/O errors,
    integrity errors)
    """
    stor_cmd = 'STOR ' + file_name
    file_url = config.ftp_download_url + file_name

    # Put the file into our FTP storage
    FTPSession = ftplib.FTP(config.ftp_server, config.ftp_user, config.ftp_password)

    try:
        FTPSession.cwd(config.ftp_upload_directory)
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

