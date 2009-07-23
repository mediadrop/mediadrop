import math
from tg import expose, validate, flash, require, url, request, response, redirect, config, tmpl_context
from tg.decorators import paginate
from tg.controllers import CUSTOM_CONTENT_TYPE
from tg.configuration import Bunch
from formencode import validators
from pylons.i18n import ugettext as _
from pylons import tmpl_context, templating
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
        tmpl_context.tags = DBSession.query(Tag)\
            .options(undefer('published_media_count'))\
            .filter(Tag.published_media_count >= 1)\
            .order_by(Tag.name)\
            .all()

    def _filter(self, query):
        """Return the query with the following filters added:

        Media are published
        Media are not trashed
        """
        return query\
            .filter(Media.status >= 'publish')\
            .filter(Media.status.excludes('trash'))

    @expose('mediaplex.templates.podcasts.index')
    def index(self, page=1, **kwargs):
        episodes_query = DBSession.query(Media)\
            .filter(Media.podcast_id != None)\
            .order_by(Media.publish_on)\
            .options(undefer('comment_count'))
        episodes_query = self._filter(episodes_query)

        # Paginate manually using our custom paginator to show fewer results on the first page
        episodes_page = custompaginate.Page(episodes_query, page, items_per_page=12, items_first_page=7)

        # Add the paginator to the tmpl_context just like tg.decorators.paginate does
        if not hasattr(tmpl_context, 'paginators') or type(tmpl_context.paginators) == str:
            tmpl_context.paginators = Bunch()
        tmpl_context.paginators.episodes = episodes_page

        return dict(
            podcasts = DBSession.query(Podcast).options(undefer('published_media_count')).all(),
            episodes = episodes_page.items,
        )


    @expose('mediaplex.templates.podcasts.view')
    @paginate('episodes', items_per_page=10)
    def view(self, slug, page=1, **kwargs):
        podcast = fetch_row(Podcast, slug=slug)
        episodes = self._filter(podcast.media)\
            .order_by(Media.publish_on.desc())

        return dict(
            podcast = podcast,
            episodes = episodes,
        )


    @expose()
    def feed(self, slug, **kwargs):
        """Serve the feed RSS.
        If a feedburner URL is defined for the podcast, we only serve the RSS
        to Feedburner (by checking the useragent), everyone else is redirected.
        """
        podcast = fetch_row(Podcast, slug=slug)

        if podcast.feedburner_url and not 'Feedburner' in request.environ['HTTP_USER_AGENT']:
            redirect(podcast.feedburner_url.encode('utf-8'))

        episodes = self._filter(podcast.media)\
            .order_by(Media.publish_on.desc())[:10]

        template_vars = dict(
            podcast = podcast,
            episodes = episodes,
        )

        # Manually render XML from genshi since tg.render.render_genshi is too stupid to support it.
        response.content_type = 'application/rss+xml'
        template_name = config['pylons.app_globals'].dotted_filename_finder.get_dotted_filename(
            'mediaplex.templates.podcasts.feed', template_extension='.xml')
        return templating.render_genshi(template_name, extra_vars=template_vars, method='xml')
