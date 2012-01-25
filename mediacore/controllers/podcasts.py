# This file is a part of MediaCore CE, Copyright 2009-2012 MediaCore Inc.
# The source code contained in this file is licensed under the GPL.
# See LICENSE.txt in the main project directory, for more information.

from paste.util import mimeparse
from pylons import config, request, response, session, tmpl_context
from repoze.what.predicates import has_permission
from sqlalchemy import orm, sql
import pylons.templating

from mediacore.lib import helpers
from mediacore.lib.base import BaseController
from mediacore.lib.decorators import (beaker_cache, expose, expose_xhr,
    observable, paginate, validate)
from mediacore.lib.helpers import redirect
from mediacore.model import Category, Media, Podcast, fetch_row
from mediacore.model.meta import DBSession
from mediacore.plugin import events

import logging
log = logging.getLogger(__name__)

class PodcastsController(BaseController):
    """
    Podcast Series Controller

    This handles episode collections, individual episodes are handled as
    regular media by :mod:`mediacore.controllers.media`.
    """

    @expose('podcasts/index.html')
    @observable(events.PodcastsController.index)
    def index(self, page=1, **kwargs):
        """List podcasts and podcast media.

        Our custom paginate decorator allows us to have fewer podcast episodes
        display on the first page than on the rest with the ``items_first_page``
        param. See :class:`mediacore.lib.custompaginate.CustomPage`.

        :param page: Page number, defaults to 1.
        :type page: int
        :rtype: dict
        :returns:
            podcasts
                The :class:`~mediacore.model.podcasts.Podcast` instance

        """
        podcasts = Podcast.query\
            .options(orm.undefer('media_count_published'))\
            .all()

        if len(podcasts) == 1:
            redirect(action='view', slug=podcasts[0].slug)

        podcast_episodes = {}
        for podcast in podcasts:
            podcast_episodes[podcast] = podcast.media.published()\
                .order_by(Media.publish_on.desc())[:4]

        return dict(
            podcasts = podcasts,
            podcast_episodes = podcast_episodes,
        )


    @expose('podcasts/view.html')
    @paginate('episodes', items_per_page=10)
    @observable(events.PodcastsController.view)
    def view(self, slug, page=1, show='latest', **kwargs):
        """View a podcast and the media that belongs to it.

        :param slug: A :attr:`~mediacore.model.podcasts.Podcast.slug`
        :param page: Page number, defaults to 1.
        :type page: int
        :rtype: dict
        :returns:
            podcast
                A :class:`~mediacore.model.podcasts.Podcast` instance.
            episodes
                A list of :class:`~mediacore.model.media.Media` instances
                that belong to the ``podcast``.
            podcasts
                A list of all the other podcasts

        """
        podcast = fetch_row(Podcast, slug=slug)
        episodes = podcast.media.published()

        episodes, show = helpers.filter_library_controls(episodes, show)

        return dict(
            podcast = podcast,
            episodes = episodes,
            result_count = episodes.count(),
            show = show,
        )

    @beaker_cache(expire=60 * 20, query_args=True)
    @expose('podcasts/feed.xml')
    @observable(events.PodcastsController.feed)
    def feed(self, slug, **kwargs):
        """Serve the feed as RSS 2.0.

        If :attr:`~mediacore.model.podcasts.Podcast.feedburner_url` is
        specified for this podcast, we redirect there if the useragent
        does not contain 'feedburner', as described here:
        http://www.google.com/support/feedburner/bin/answer.py?hl=en&answer=78464

        :param feedburner_bypass: If true, the redirect to feedburner is disabled.
        :rtype: Dict
        :returns:
            podcast
                A :class:`~mediacore.model.podcasts.Podcast` instance.
            episodes
                A list of :class:`~mediacore.model.media.Media` instances
                that belong to the ``podcast``.

        Renders: :data:`podcasts/feed.xml` XML

        """
        podcast = fetch_row(Podcast, slug=slug)

        if (podcast.feedburner_url
            and not 'feedburner' in request.environ.get('HTTP_USER_AGENT', '').lower()
            and not kwargs.get('feedburner_bypass', False)):
            redirect(podcast.feedburner_url.encode('utf-8'))

        # Choose the most appropriate content_type for the client
        response.content_type = mimeparse.best_match(
            ['application/rss+xml', 'application/xml', 'text/xml'],
            request.environ.get('HTTP_ACCEPT', '*/*')
        )

        episodes = podcast.media.published()\
            .order_by(Media.publish_on.desc())[:25]

        return dict(
            podcast = podcast,
            episodes = episodes,
        )
