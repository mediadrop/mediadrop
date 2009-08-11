"""
Video Controller

"""
import math
import shutil
import os.path
import simplejson as json
import time

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

        # save the object to our database to get an ID
        DBSession.add(video)
        DBSession.flush()

        # set up the permanent filename for this upload
        file_name = '-'.join((str(video.id), email, file.filename))
        file_name = file_name.lstrip(os.path.sep)
        file_type = os.path.splitext(file_name)[1].lower()[1:]

        # set the file paths depending on the file type
        media_file = MediaFile()
        media_file.type = file_type
        media_file.url = file_name
        media_file.is_original = True

        # copy the file to its permanent location
        file_path = os.path.join(config.media_dir, file_name)
        permanent_file = open(file_path, 'w')
        shutil.copyfileobj(file.file, permanent_file)
        file.file.close()
        media_file.size = os.fstat(permanent_file.fileno())[6]
        permanent_file.close()

        # update video relations
        video.files.append(media_file)
        if file_type == 'flv':
            video.status.discard('unencoded')

        video.set_tags(tags)

        DBSession.add(video)
        DBSession.flush()

        return video
