import math
from tg import expose, validate, flash, require, url, request, response, redirect, config, tmpl_context
from tg.decorators import paginate
from tg.controllers import CUSTOM_CONTENT_TYPE
from tg.configuration import Bunch
from formencode import validators
from pylons.i18n import ugettext as _
from pylons import tmpl_context
from sqlalchemy import and_, or_
from sqlalchemy.orm import eagerload, undefer

from mediaplex.lib import helpers, custompaginate
from mediaplex.lib.helpers import expose_xhr, redirect, url_for
from mediaplex.lib.base import Controller, RoutingController
from mediaplex.model import DBSession, fetch_row, Podcast, Media, Tag

class PodcastsController(RoutingController):
    """Podcast actions -- episodes are handled in the MediaController"""

    def __init__(self, *args, **kwargs):
        super(PodcastsController, self).__init__(*args, **kwargs)
        tmpl_context.podcast_help = True
        tmpl_context.tags = DBSession.query(Tag)\
            .options(undefer('media_count'))\
            .filter(Tag.media_count >= 1)\
            .order_by(Tag.name)\
            .all()


    @expose('mediaplex.templates.podcasts.index')
    def index(self, page=1, **kwargs):
        episodes_query = DBSession.query(Media)\
            .filter(Media.podcast_id != None)\
            .filter(Media.status >= 'publish')\
            .filter(Media.status.excludes('trash'))\
            .order_by(Media.publish_on)\
            .options(undefer('comment_count'))

        # Paginate manually using our custom paginator to show fewer results on the first page
        episodes_page = custompaginate.Page(episodes_query, page, items_per_page=12, items_first_page=7)

        # Add the paginator to the tmpl_context just like tg.decorators.paginate does
        if not hasattr(tmpl_context, 'paginators') or type(tmpl_context.paginators) == str:
            tmpl_context.paginators = Bunch()
        tmpl_context.paginators.episodes = episodes_page

        return dict(
            podcasts = DBSession.query(Podcast).options(undefer('media_count')).all(),
            episodes = episodes_page.items
        )


    @expose('mediaplex.templates.podcasts.view')
    @paginate('episodes', items_per_page=10)
    def view(self, slug, page=1, **kwargs):
        podcast = fetch_row(Podcast, slug=slug)
        return dict(
            podcast = podcast,
            episodes = podcast.media,
        )


    @expose('mediaplex.templates.podcasts.feed', content_type=CUSTOM_CONTENT_TYPE)
    def feed(self, slug, **kwargs):
        podcast = fetch_row(Podcast, slug=slug)
        response.content_type = 'application/rss+xml'
        return dict(
            podcast = podcast,
        )
