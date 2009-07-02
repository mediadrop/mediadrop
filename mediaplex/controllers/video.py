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
from formencode import validators
from pylons.i18n import ugettext as _
from sqlalchemy import and_, or_
from sqlalchemy.orm import eagerload, undefer

from mediaplex.lib import helpers
from mediaplex.lib.helpers import expose_xhr, redirect, url_for, clean_xhtml
from mediaplex.lib.base import Controller, RoutingController
from mediaplex.model import DBSession, metadata, fetch_row, Video, Media, MediaFile, Comment, Tag, Author, AuthorWithIP
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
        tmpl_context.tags = DBSession.query(Tag)\
            .options(undefer('media_count'))\
            .filter(Tag.media_count >= 1)\
            .order_by(Tag.name)\
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
            videos = self._list_query.order_by(Video.publish_on.desc())[:15],
        )


    @property
    def _list_query(self):
        """Helper method for paginating video results"""
        return DBSession.query(Video)\
            .filter(Video.status >= 'publish')\
            .filter(Video.publish_on <= datetime.now())\
            .filter(Video.status.excludes('trash'))\
            .filter(Video.podcast_id == None)


    @expose('mediaplex.templates.video.index')
    @paginate('videos', items_per_page=20)
    def tags(self, slug=None, page=1, **kwargs):
        tag = DBSession.query(Tag).filter(Tag.slug == slug).one()
        video_query = self._list_query\
            .filter(Video.tags.contains(tag))\
            .options(undefer('comment_count'))
        tmpl_context.show_tags = True
        return dict(
            videos = video_query,
        )


    @expose('mediaplex.templates.video.upload')
    @validate(upload_form)
    def upload(self, **kwargs):
        return dict(
            upload_form = upload_form,
            form_values = kwargs,
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
            self._save_video(kwargs['name'], kwargs['email'], kwargs['title'], kwargs['description'], kwargs['tags'], kwargs['file'])

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
        self._save_video(kwargs['name'], kwargs['email'], kwargs['title'], kwargs['description'], kwargs['tags'], kwargs['file'])

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
        video = Video()
        video.author = Author(name, email)
        video.title = title
        video.slug = title
        video.description = clean_xhtml(description)
        video.status = 'draft,unencoded,unreviewed'
        video.notes = """Bible References: None
S&H References: None
Reviewer: None
License: General Upload"""

        # ensure the slug is unique by appending an int in sequence
        slug_appendix = 2
        while DBSession.query(Video.id).filter(Video.slug == video.slug).first():
            video.slug = video.slug[:-1-int(math.ceil(math.log10(slug_appendix)))]
            video.slug += '-' + str(slug_appendix)
            slug_appendix += 1

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
