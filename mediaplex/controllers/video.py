"""
Video/Media Controller

"""
import shutil
import os.path
import simplejson as json
import time

from urlparse import urlparse, urlunparse
from cgi import parse_qs
from PIL import Image
from datetime import datetime
from tg import expose, validate, decorators, flash, require, url, request, redirect, config
from formencode import validators
from pylons.i18n import ugettext as _
from pylons import tmpl_context
from sqlalchemy import and_, or_
from sqlalchemy.orm import eagerload
from webhelpers import paginate

from mediaplex.lib import helpers
from mediaplex.lib.helpers import expose_xhr
from mediaplex.lib.base import Controller, RoutingController
from mediaplex.model import DBSession, metadata, Video, Comment, Tag, Author, AuthorWithIP
from mediaplex.forms.admin import SearchForm
from mediaplex.forms.video import VideoForm, AlbumArtForm, UploadForm
from mediaplex.forms.comments import PostCommentForm

upload_form = UploadForm(
    action = helpers.url_for(action='upload_submit'),
    async_action = helpers.url_for(action='upload_submit_async')
)


class VideoController(RoutingController):
    """Public video list actions"""

    @expose('mediaplex.templates.video.index')
    def index(self, page=1, **kwargs):
        """Grid-style List Action"""
        return dict(page=self._fetch_page(page, 25), tags=self._fetch_tags())

    @expose('mediaplex.templates.video.mediaflow')
    def flow(self, page=1, **kwargs):
        """Mediaflow Action"""
        return dict(page=self._fetch_page(page, 9), tags=self._fetch_tags())

    @expose('mediaplex.templates.video.mediaflow-ajax')
    def flow_ajax(self, page=1, **kwargs):
        """Mediaflow Ajax Fetch Action"""
        return dict(page=self._fetch_page(page, 6))

    def _fetch_page(self, page_num=1, items_per_page=25, query=None):
        """Helper method for paginating video results"""
        query = query or DBSession.query(Video).\
            filter(Video.status >= 'publish').\
            filter(Video.publish_on <= datetime.now()).\
            filter(Video.status.excludes('trash'))
        return paginate.Page(query, page_num, items_per_page)

    @expose('mediaplex.templates.video.index')
    def tags(self, slug=None, page=1, **kwargs):
        tag = DBSession.query(Tag).filter(Tag.slug == slug).one()
        query = DBSession.query(Video)\
            .filter(Video.tags.contains(tag))\
            .filter(Video.status.excludes('trash'))
        return dict(page=self._fetch_page(page, 25, query=query), tags=self._fetch_tags(), show_tags=True)

    def _fetch_tags(self):
        return DBSession.query(Tag).order_by(Tag.name).all()

    @expose('mediaplex.templates.video.view')
    def view(self, slug, **values):
        video = self._fetch_video(slug)
        video.views += 1
        DBSession.add(video)
        form = PostCommentForm(action=helpers.url_for(action='comment', slug=video.slug))
        return dict(
            video=video,
            comment_form=form,
            form_values=values,
            tags=self._fetch_tags()
        )

    @expose_xhr()
    @validate(validators=dict(rating=validators.Int()))
    def rate(self, slug, rating, **kwargs):
        video = self._fetch_video(slug)

        if rating > 0:
            video.rating.add_vote(1)
        else:
            video.rating.add_vote(0)

        DBSession.add(video)
        if request.is_xhr:
            return dict(
                rating='%d/%d' % (video.rating.sum, video.rating.votes),
                success=True
            )
        else:
            redirect(helpers.url_for(action='view', slug=video.slug))

    @expose()
    @validate(PostCommentForm(), error_handler=view)
    def comment(self, slug, **values):
        video = self._fetch_video(slug)
        c = Comment()
        c.status = 'pending_review'
        c.author = AuthorWithIP(values['name'], None, request.environ['REMOTE_ADDR'])
        c.subject = 'Re: %s' % video.title
        c.body = values['body']
        video.comments.append(c)
        DBSession.add(video)
        redirect(helpers.url_for(action='view', slug=video.slug))

    def _fetch_video(self, slug):
        return DBSession.query(Video)\
            .filter(Video.slug == slug)\
            .filter(Video.status.excludes('trash'))\
            .one()

    @expose('mediaplex.templates.video.upload')
    @validate(upload_form)
    def upload(self, **kwargs):
        form_values = dict(
            tags = 'video'
        )
        form_values.update(kwargs)

        return dict(
            tags = self._fetch_tags(),
            upload_form = upload_form,
            form_values = form_values
        )

    @expose('json')
    @validate(upload_form)
    def upload_submit_async(self, **kwargs):
        if 'validate' in kwargs:
            # we're just validating the fields. no need to worry.
            fields = json.loads(kwargs['validate'])
            err = {}
            for field in fields:
                print "Validating:", field
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
            self._save_video(kwargs['name'], kwargs['email'], kwargs['title'], kwargs['description'], kwargs['tags'], kwargs['file'])

            return dict(
                success = True
            )

    @expose()
    @validate(upload_form, error_handler=upload)
    def upload_submit(self, **kwargs):
        if 'name' not in kwargs:
            kwargs['name'] = None

        # Save the video!
        self._save_video(kwargs['name'], kwargs['email'], kwargs['title'], kwargs['description'], kwargs['tags'], kwargs['file'])

        # Redirect to success page!
        redirect(helpers.url_for(action='upload_success'))

    @expose()
    def upload_success(self, **kwargs):
        return dict()

    def _save_video(self, name, email, title, description, tags, file):
        # cope with anonymous posters
        if name is None:
            name = 'Anonymous'

        # set up the permanent filename for this upload
        file_name = str(int(time.time())) + '_' + email + '_' + file.filename
        file_name = file_name.lstrip(os.sep)

        # create our video object
        video = Video()
        video.author = Author(name, email)
        video.encode_url = file_name
        video.slug = file_name
        video.title = title
        video.description = description
        video.set_tags(tags)
        video.status.add('pending_review')

        # Copy the file to its permanent location
        file_path = os.sep.join([config.media_dir, file_name])
        permanent_file = open(file_path, 'w')
        shutil.copyfileobj(file.file, permanent_file)
        file.file.close()
        permanent_file.close()

        # Save the object to our database
        DBSession.add(video)
        DBSession.flush()

