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
from tg.exceptions import HTTPNotFound
from tg.decorators import paginate
from tg.controllers import CUSTOM_CONTENT_TYPE
from formencode import validators
from pylons.i18n import ugettext as _
from sqlalchemy import and_, or_
from sqlalchemy.orm import eagerload, undefer

from mediaplex.lib import helpers
from mediaplex.lib.helpers import expose_xhr, redirect
from mediaplex.lib.base import Controller, RoutingController
from mediaplex.model import DBSession, metadata, Video, Media, MediaFile, Comment, Tag, Author, AuthorWithIP
from mediaplex.forms.media import UploadForm
from mediaplex.forms.comments import PostCommentForm


class MediaController(RoutingController):
    """Media actions -- for both regular and podcast media"""

    def __init__(self, *args, **kwargs):
        super(MediaController, self).__init__(*args, **kwargs)
        tmpl_context.tags = DBSession.query(Tag)\
            .options(undefer('media_count'))\
            .filter(Tag.media_count >= 1)\
            .order_by(Tag.name)\
            .all()


    @expose('mediaplex.templates.media.view')
    def view(self, slug, podcast_slug=None, **kwargs):
        """Display the media player and comments"""
        media = self._fetch_media(slug)

        if media.podcast_id is not None:
            # Always view podcast media from a URL that shows the context of the podcast
            if helpers.url_for() != helpers.url_for(podcast_slug=media.podcast.slug):
               redirect(podcast_slug=media.podcast.slug)

            tmpl_context.podcast_help = True
            next_episode = DBSession.query(Media)\
                .filter(Media.podcast_id == media.podcast.id)\
                .filter(Media.publish_on > media.publish_on)\
                .filter(Media.publish_on < datetime.now())\
                .filter(Media.status >= 'publish')\
                .filter(Media.status.excludes('trash'))\
                .order_by(Media.publish_on)\
                .first()
        else:
            next_episode = None

        return dict(
            media = media,
            comment_form = PostCommentForm(action=helpers.url_for(action='comment')),
            comment_form_values = kwargs,
            next_episode = next_episode,
        )


    @expose_xhr()
    @validate(validators=dict(rating=validators.Int()))
    def rate(self, slug, rating=1, **kwargs):
        media = self._fetch_media(slug)

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
    @validate(PostCommentForm(), error_handler=view)
    def comment(self, slug, **values):
        media = self._fetch_media(slug)
        c = Comment()
        c.status = 'unreviewed'
        c.author = AuthorWithIP(values['name'], None, request.environ['REMOTE_ADDR'])
        c.subject = 'Re: %s' % media.title
        c.body = values['body']
        media.comments.append(c)
        DBSession.add(media)
        redirect(action='view')


    @expose()
    def serve(self, slug, type=None, **kwargs):
        media = self._fetch_media(slug)
        if type is None:
            type = media.ENCODED_TYPE
        for file in (file for file in media.files if file.type == type):
            file_path = os.path.join(config.media_dir, file.url)
            file_handle = open(file_path, 'rb')
            response.content_type = config.mimetype_lookup.get('.' + file.type, 'application/octet-stream')
            return file_handle.read()
        else:
            raise HTTPNotFound()


    def _fetch_media(self, slug):
        return DBSession.query(Media)\
            .filter(Media.slug == slug)\
            .filter(Media.status.excludes('trash'))\
            .one()
