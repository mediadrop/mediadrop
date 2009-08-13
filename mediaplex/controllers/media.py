import math
import shutil
import os.path
import simplejson as json
import time

from urlparse import urlparse, urlunparse
from cgi import parse_qs
from PIL import Image
from datetime import datetime, timedelta, date
from tg import expose, validate, flash, require, url, request, response, config, tmpl_context
from tg.exceptions import HTTPNotFound
from tg.decorators import paginate
from tg.controllers import CUSTOM_CONTENT_TYPE
from formencode import validators
from pylons.i18n import ugettext as _
from sqlalchemy import and_, or_
from sqlalchemy.orm import eagerload, undefer
from sqlalchemy.orm.exc import NoResultFound

from mediaplex.lib import helpers, email
from mediaplex.lib.helpers import expose_xhr, redirect, url_for, clean_xhtml, strip_xhtml, line_break_xhtml
from mediaplex.lib.base import Controller, RoutingController
from mediaplex.model import DBSession, metadata, fetch_row, Media, MediaFile, Comment, Topic, Author, AuthorWithIP, Podcast
from mediaplex.forms.media import UploadForm
from mediaplex.forms.comments import PostCommentForm


class MediaController(RoutingController):
    """Media actions -- for both regular and podcast media"""

    def __init__(self, *args, **kwargs):
        super(MediaController, self).__init__(*args, **kwargs)
        tmpl_context.topics = DBSession.query(Topic)\
            .options(undefer('published_media_count'))\
            .filter(Topic.published_media_count >= 1)\
            .order_by(Topic.name)\
            .all()

    @expose('mediaplex.templates.media.index')
    @paginate('media', items_per_page=20)
    def index(self, page=1, topics=None, **kwargs):
        """Grid-style List Action"""
        media = DBSession.query(Media)\
            .filter(Media.status >= 'publish')\
            .filter(Media.publish_on <= datetime.now())\
            .filter(Media.status.excludes('trash'))\
            .filter(Media.podcast_id == None)\
            .order_by(Media.publish_on.desc())\
            .options(undefer('comment_count'))

        return dict(
            media = media,
        )

    @expose('mediaplex.templates.media.lessons')
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
                .options(undefer('comment_count'))
        except HTTPNotFound:
            media = []

        today = date.today()
        sunday = today - timedelta(days=today.weekday()+1)
        sunday = datetime(sunday.year, sunday.month, sunday.day)

        return dict(
            media = media,
            week_start = sunday,
        )

    @expose('mediaplex.templates.media.lesson_view')
    def lesson_view(self, slug, **kwargs):
        """Display the media player and comments"""
        media = fetch_row(Media, slug=slug)
        next_episode = None
        media.views += 1

        return dict(
            media = media,
            comment_form = PostCommentForm(action=url_for(action='lesson_comment')),
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

    @expose('mediaplex.templates.media.view')
    def view(self, slug, podcast_slug=None, **kwargs):
        """Display the media player and comments"""
        media = fetch_row(Media, slug=slug)
        media.views += 1

        if media.podcast_id is not None:
            # Always view podcast media from a URL that shows the context of the podcast
            if url_for() != url_for(podcast_slug=media.podcast.slug):
               redirect(podcast_slug=media.podcast.slug)

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
            comment_form = PostCommentForm(action=url_for(action='comment')),
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
        )

    @expose('mediaplex.templates.media.concept_view')
    def concept_view(self, slug, podcast_slug=None, **kwargs):
        """Display the media player and comments"""
        media = fetch_row(Media, slug=slug)
        media.views += 1

        return dict(
            media = media,
            comment_form = PostCommentForm(action=url_for(action='concept_comment')),
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
    @validate(PostCommentForm(), error_handler=view)
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
    def serve(self, slug, type=None, **kwargs):
        media = fetch_row(Media, slug=slug)
        if type is None:
            type = media.ENCODED_TYPE
        for file in (file for file in media.files if file.type == type):
            file_path = os.path.join(config.media_dir, file.url)
            file_handle = open(file_path, 'rb')
            response.content_type = file.mimetype
            return file_handle.read()
        else:
            raise HTTPNotFound()

