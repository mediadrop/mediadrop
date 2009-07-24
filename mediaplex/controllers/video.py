"""
Video Controller

"""
import math
import shutil
import os.path
import simplejson as json
import time
import smtplib

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
from sqlalchemy.orm.exc import NoResultFound

from mediaplex.lib import helpers
from mediaplex.lib.helpers import expose_xhr, redirect, url_for, clean_xhtml, strip_xhtml, line_break_xhtml
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
            .options(undefer('published_media_count'))\
            .filter(Tag.published_media_count >= 1)\
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
            videos = self._list_query[:15],
        )

    @expose('mediaplex.templates.video.concept_preview')
    def concept_preview(self, page=1, **kwargs):
        """Mediaflow Action"""
        tmpl_context.disable_topics = True
        tmpl_context.disable_sections = True
        videos = []
        try:
            tag = DBSession.query(Tag).filter(Tag.slug == 'conceptsundayschool').one()
            videos = self._list_query.filter(Video.tags.contains(tag)).order_by(Video.publish_on.desc())[:15]
        except NoResultFound, e:
            pass

        return dict(
            videos = videos
        )

    @property
    def _list_query(self):
        """Helper method for paginating video results"""
        return DBSession.query(Video)\
            .filter(Video.status >= 'publish')\
            .filter(Video.publish_on <= datetime.now())\
            .filter(Video.status.excludes('trash'))\
            .filter(Video.podcast_id == None)\
            .order_by(Video.publish_on.desc())


    @expose('mediaplex.templates.video.index')
    @paginate('videos', items_per_page=20)
    def tags(self, slug=None, page=1, **kwargs):
        tag = DBSession.query(Tag).filter(Tag.slug == slug).one()
        video_query = self._list_query\
            .filter(Video.tags.contains(tag))\
            .options(undefer('comment_count'))
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

            video = self._save_video(
                kwargs['name'], kwargs['email'],
                kwargs['title'], kwargs['description'],
                kwargs['tags'], kwargs['file']
            )
            self._send_notification(video)

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
        self._send_notification(video)

        # Redirect to success page!
        redirect(action='upload_success')


    @expose('mediaplex.templates.video.upload-success')
    def upload_success(self, **kwargs):
        return dict()


    @expose('mediaplex.templates.video.upload-failure')
    def upload_failure(self, **kwargs):
        return dict()

    def _send_notification(self, video):
        server=smtplib.SMTP('localhost')
        fr = 'noreply@tmcyouth.com'
        to = 'anthony@simplestation.com'
        subject = 'New Video: %s' % video.title
        body = """A new video has been uploaded!

Title: %s

Author: %s (%s)

Admin URL: %s

Description: %s
""" % (video.title, video.author.name, video.author.email,
       url_for(controller='mediaadmin', action='edit', id=video.id),
       strip_xhtml(line_break_xhtml(line_break_xhtml(video.description))))

        msg = """To: %s
From: %s
Subject: %s

%s
""" % (to, fr, subject, body)

        server.sendmail(fr, to, msg)
        server.quit()

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

        return video
