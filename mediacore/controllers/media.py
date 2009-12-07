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
Publicly Facing Media Controllers
"""
import shutil
import os.path
import simplejson as json
import ftplib
import urllib2
import sha
import time
from urlparse import urlparse
from datetime import datetime, timedelta, date

from tg import config, request, response, tmpl_context, exceptions
from tg.controllers import CUSTOM_CONTENT_TYPE
from sqlalchemy import orm, sql
from formencode import validators
from paste.deploy.converters import asbool

from mediacore.lib.base import (BaseController, url_for, redirect,
    expose, expose_xhr, validate, paginate)
from mediacore.model import (DBSession, fetch_row, get_available_slug,
    Media, MediaFile, Comment, Tag, Topic, Author, AuthorWithIP, Podcast)
from mediacore.lib import helpers, email
from mediacore.forms.media import UploadForm
from mediacore.forms.comments import PostCommentForm


post_comment_form = PostCommentForm()
upload_form = UploadForm(
    action = url_for(controller='/media', action='upload_submit'),
    async_action = url_for(controller='/media', action='upload_submit_async')
)


class FTPUploadException(Exception):
    pass


class MediaController(BaseController):
    """Media actions -- for both regular and podcast media"""

    def __init__(self, *args, **kwargs):
        """Populate the :obj:`pylons.tmpl_context`` with topics.

        Used by :data:`mediacore.templates.helpers` to render the
        topic index flyout slider.

        """
        super(MediaController, self).__init__(*args, **kwargs)
        tmpl_context.topics = DBSession.query(Topic)\
            .options(orm.undefer('published_media_count'))\
            .having(sql.text('published_media_count >= 1'))\
            .order_by(Topic.name)\
            .all()


    @expose('mediacore.templates.media.index')
    @paginate('media', items_per_page=20)
    def index(self, page=1, **kwargs):
        """List media with pagination.

        The media paginator may be accessed in the template with
        :attr:`c.paginators.media`, see :class:`webhelpers.paginate.Page`.

        :param page: Page number, defaults to 1.
        :type page: int
        :rtype: dict
        :returns:
            media
                The list of :class:`~mediacore.model.media.Media` instances
                for this page.

        """
        return dict(
            media = self._list_query.options(orm.undefer('comment_count')),
        )


    @expose('mediacore.templates.media.view')
    def view(self, slug, podcast_slug=None, **kwargs):
        """Display the media player, info and comments.

        :param slug: The :attr:`~mediacore.models.media.Media.slug` to lookup
        :param podcast_slug: The :attr:`~mediacore.models.podcasts.Podcast.slug`
            for podcast this media belongs to. Although not necessary for
            looking up the media, it tells us that the podcast slug was
            specified in the URL and therefore we reached this action by the
            preferred route.
        :rtype dict:
        :returns:
            media
                The :class:`~mediacore.model.media.Media` instance for display.
            comment_form
                The :class:`~mediacore.forms.comments.PostCommentForm` instance.
            comment_form_action
                ``str`` comment form action
            comment_form_values
                ``dict`` form values
            next_episode
                The next episode in the podcast series, if this media belongs to
                a podcast, another :class:`~mediacore.model.media.Media`
                instance.

        """
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
    def latest(self, type=None, podcast=None, ignore=None,
               topic=None, tag=None, **kwargs):
        """Expose basic info of the latest media object.

        .. todo:: Work this into a more general, documented API scheme.

        :param type: ``audio``, ``video``, or ``None`` for either
        :param podcast: A :attr:`simpleplx.modelpodcast slug or empty string
        :param topic: A topic slug
        :param ignore: An id to always exclude from results.
            this allows us to fetch two DIFFERENT results
            when calling this action twice.
        :rtype: JSON dict

        """
        media_query = self._published_media_query

        if type:
            media_query = media_query.filter(Media.type == type)

        # Filter by podcast, if podcast slug provided
        if podcast != None:
            if podcast == '':
                media_query = media_query\
                    .filter(Media.podcast_id == None)
            else:
                podcast = fetch_row(Podcast, slug=podcast)
                media_query = media_query\
                    .filter(Media.podcast_id == podcast.id)

        # Filter by topic, if topic slug provided
        if topic:
            topic = fetch_row(Topic, slug=topic)
            media_query = media_query\
                .filter(Media.topics.contains(topic))

        # Filter by tag, if tag slug provided
        if tag:
            tag = fetch_row(Tag, slug=tag)
            media_query = media_query\
                .filter(Media.tags.contains(tag))

        # Filter out a media item we don't like
        if ignore:
            media_query = media_query.filter(Media.slug != ignore)

        # get the actual object (hope there is one!)
        media = media_query.first()

        return self._jsonify(media)

    @expose('json')
    def most_popular(self, **kwargs):
        """Expose basic info of the latest media object.

        .. todo:: Work this into a more general, documented API scheme.

        :rtype: JSON dict

        """
        media_query = DBSession.query(Media)\
            .filter(Media.status >= 'publish')\
            .filter(Media.publish_on <= datetime.now())\
            .filter(Media.status.excludes('trash'))\
            .order_by(Media.views.desc())

        media = media_query.first()
        return self._jsonify(media)

    def _jsonify(self, media):
        im_path = '/images/media/%d%%s.jpg' % media.id

        if media.podcast_id:
            media_url = url_for(controller='/media', action='view', slug=media.slug,
                                podcast_slug=media.podcast.slug)
        else:
            media_url = url_for(controller="/media", action="view", slug=media.slug)

        return dict(
            title = media.title,
            description = media.description,
            description_plain = helpers.strip_xhtml(helpers.line_break_xhtml(\
                helpers.line_break_xhtml(media.description))),
            img_l = url_for(im_path % 'l'),
            img_m = url_for(im_path % 'm'),
            img_s = url_for(im_path % 's'),
            img_ss = url_for(im_path % 'ss'),
            id = media.id,
            slug = media.slug,
            url = media_url,
            podcast = media.podcast and media.podcast.slug or None,
        )

    @expose_xhr()
    @validate(validators=dict(rating=validators.Int()))
    def rate(self, slug, rating=1, **kwargs):
        """Rate up or down the given media.

        :param slug: The media :attr:`~mediacore.model.media.Media.slug`
        :param rating: ``1`` or ``0`` if the rating is up or down.
        :rtype: JSON dict
        :returns:
            succcess
                bool
            upRating
                Pluralized count of up raters, "# people" or "1 person"
            downRating
                Pluralized count of down raters, "# people" or "1 person"

        """
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


    @expose('json')
    @validate(post_comment_form)
    def comment(self, slug, **values):
        """Post a comment from :class:`~mediacore.forms.media.PostCommentForm`.

        :param slug: The media :attr:`~mediacore.model.media.Media.slug`
        :returns: Redirect to :meth:`view` page for media.

        """
        if tmpl_context.form_errors:
            if request.is_xhr:
                return dict(
                    success = False,
                    errors = tmpl_context.form_errors
                )
            else:
                redirect(action='view')

        media = fetch_row(Media, slug=slug)
        c = Comment()
        c.status = 'unreviewed'
        c.author = AuthorWithIP(values['name'], None, request.environ['REMOTE_ADDR'])
        c.subject = 'Re: %s' % media.title
        c.body = helpers.clean_xhtml(values['body'])

        media.comments.append(c)
        DBSession.add(media)
        email.send_comment_notification(media, c)

        if request.is_xhr:
            return dict(success = True)
        else:
            redirect(action='view')


    @expose(content_type=CUSTOM_CONTENT_TYPE)
    @validate(validators={'id': validators.Int()})
    def serve(self, id, slug, type, **kwargs):
        """Serve a :class:`~mediacore.model.media.MediaFile` binary.

        :param id: File ID
        :type id: ``int``
        :param slug: The media :attr:`~mediacore.model.media.Media.slug`
        :type slug: The file :attr:`~mediacore.model.media.MediaFile.type`
        :raises tg.exceptions.HTTPNotFound: If no file exists for the given params.

        """
        media = fetch_row(Media, slug=slug)

        for file in media.files:
            if file.id == id and file.type == type:
                # Redirect to an external URL
                if urlparse(file.url)[1]:
                    redirect(file.url.encode('utf-8'))
                file_name = '%s-%s.%s' % (media.slug, file.id, file.type)
                file_path = os.path.join(config.media_dir, file.url)
                file_handle = open(file_path, 'rb')
                response.content_type = file.mimetype
# FIXME: Determine how to set this header properly
#                request['Content-Disposition'] = \
#                    'attachment;filename=%s' % file_name
                return file_handle.read()
        else:
            raise exceptions.HTTPNotFound()

    @expose('mediacore.templates.media.mediaflow')
    def flow(self, page=1, **kwargs):
        """Display the most recent 15 media.

        :rtype: Dict
        :returns:
            media
                Latest media

        """
        return dict(
            media = self._list_query[:15],
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


    @expose('mediacore.templates.media.topics')
    @paginate('media', items_per_page=20)
    def topics(self, slug=None, page=1, **kwargs):
        if slug:
            topic = fetch_row(Topic, slug=slug)
            media_query = self._published_media_query\
                .filter(Media.topics.contains(topic))\
                .options(orm.undefer('comment_count_published'))
            media = media_query
        else:
            topic = None
            media = []

        return dict(
            media = media,
            topic = topic,
        )

    @expose('mediacore.templates.media.tags')
    @paginate('media', items_per_page=20)
    def tags(self, slug=None, page=1, **kwargs):
        if slug:
            tag = fetch_row(Tag, slug=slug)
            media_query = self._published_media_query\
                .filter(Media.tags.contains(tag))\
                .options(orm.undefer('comment_count_published'))
            media = media_query
            tags = None
        else:
            tag = None
            media = []
            tags = DBSession.query(Tag)\
                .options(orm.undefer('published_media_count'))\
                .having(sql.text('published_media_count >= 1'))\
                .order_by(Tag.name)\
                .all()

        return dict(
            media = media,
            tag = tag,
            tags = tags,
        )

    @expose('mediacore.templates.media.upload')
    def upload(self, **kwargs):
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
        support_emails = helpers.fetch_setting('email_support_requests')
        support_emails = email.parse_email_string(support_emails)
        support_email = support_emails and support_emails[0] or None

        return dict(
            legal_wording = helpers.fetch_setting('wording_user_uploads'),
            support_email = support_email,
            upload_form = upload_form,
            form_values = {},
        )

    @expose()
    @validate(upload_form)
    def upload_submit_async(self, **kwargs):
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

            This method returns incorrect Content-type headers. It should
            return ``application/json``, but we return ``text/html``. There
            seems to be a bug in TG 2.0.x wrt setting the content type
            that was giving inconsistent results when trying to set
            ``text/plain``.

            Swiff.Uploader (which we use) uses Flash's FileReference.upload()
            method, which doesn't allow overriding the HTTP headers.
            On windows, the default headers have an "Accept: text/*" line.
            This means that it won't accept "application/json".
            TG Honours that, and, when returning, will throw an error rather
            than return an invalid content-type.

        """
        if 'validate' in kwargs:
            # we're just validating the fields. no need to worry.
            fields = json.loads(kwargs['validate'])
            err = {}
            for field in fields:
                if field in tmpl_context.form_errors:
                    err[field] = tmpl_context.form_errors[field]

            return json.dumps(dict(
                valid = len(err) == 0,
                err = err
            ))
        else:
            # We're actually supposed to save the fields. Let's do it.
            if len(tmpl_context.form_errors) != 0:
                # if the form wasn't valid, return failure
                return json.dumps(dict(
                    success = False
                ))

            # else actually save it!
            kwargs.setdefault('name')
            kwargs.setdefault('tags')

            media_obj = self._save_media_obj(
                kwargs['name'], kwargs['email'],
                kwargs['title'], kwargs['description'],
                kwargs['tags'], kwargs['file']
            )
            email.send_media_notification(media_obj)

            return json.dumps(dict(
                success = True,
                redirect = url_for(action='upload_success')
            ))


    @expose()
    @validate(upload_form, error_handler=upload)
    def upload_submit(self, **kwargs):
        """
        """
        kwargs.setdefault('name')
        kwargs.setdefault('tags')

        # Save the media_obj!
        media_obj = self._save_media_obj(
            kwargs['name'], kwargs['email'],
            kwargs['title'], kwargs['description'],
            kwargs['tags'], kwargs['file']
        )
        email.send_media_notification(media_obj)

        # Redirect to success page!
        redirect(action='upload_success')


    @expose('mediacore.templates.media.upload-success')
    def upload_success(self, **kwargs):
        return dict()


    @expose('mediacore.templates.media.upload-failure')
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
        media_obj.description = helpers.clean_xhtml(description)
        media_obj.status = 'draft,unencoded,unreviewed'
        media_obj.notes = (
            u"Bible References: None\n"
            u"S&H References: None\n"
            u"Reviewer: None\n"
            u"License: General Upload\n"
        )
        media_obj.set_tags(tags)

        # Create a media object, add it to the media_obj, and store the file permanently.
        media_file = _add_new_media_file(media_obj, file.filename, file.file)

        # Add the final changes.
        media_obj.update_type()
        media_obj.update_status()
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
    if asbool(config.ftp_storage):
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
    FTPSession = ftplib.FTP(config.ftp_server,
                            config.ftp_username,
                            config.ftp_password)

    try:
        FTPSession.cwd(config.ftp_upload_path)
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

