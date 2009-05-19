"""
Video/Media Controller

"""
import shutil
import os.path
from urlparse import urlparse, urlunparse
from cgi import parse_qs
from PIL import Image
from datetime import datetime
from tg import expose, validate, decorators, flash, require, url, request, redirect
from formencode import validators
from pylons.i18n import ugettext as _
from sqlalchemy import and_, or_
from sqlalchemy.orm import eagerload
from webhelpers import paginate

from mediaplex.lib import helpers
from mediaplex.lib.helpers import expose_xhr
from mediaplex.lib.base import Controller, RoutingController
from mediaplex.model import DBSession, metadata, Video, Comment, Tag, Author, AuthorWithIP
from mediaplex.forms.admin import SearchForm
from mediaplex.forms.video import VideoForm, AlbumArtForm
from mediaplex.forms.comments import PostCommentForm


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
        query = DBSession.query(Video).filter(Video.tags.contains(tag))
        return dict(page=self._fetch_page(page, 25, query=query), tags=self._fetch_tags(), show_tags=True)

    def _fetch_tags(self):
        return DBSession.query(Tag).order_by(Tag.name).all()

    @expose('mediaplex.templates.video.view')
    def view(self, slug, **values):
        video = DBSession.query(Video).filter_by(slug=slug).one()
        video.views += 1
        DBSession.add(video)
        form = PostCommentForm(action=helpers.url_for(action='comment', slug=video.slug))
        return dict(
            video=video,
            comment_form=form,
            form_values=values
        )

    @expose_xhr()
    @validate(validators=dict(rating=validators.Int()))
    def rate(self, slug, rating, **kwargs):
        video = DBSession.query(Video).filter_by(slug=slug).one()

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
        video = DBSession.query(Video).filter_by(slug=slug).one()
        c = Comment()
        c.status = 'pending_review'
        c.author = AuthorWithIP(values['name'], None, request.environ['REMOTE_ADDR'])
        c.subject = 'Re: %s' % video.title
        c.body = values['body']
        video.comments.append(c)
        DBSession.add(video)
        redirect(helpers.url_for(action='view', slug=video.slug))
