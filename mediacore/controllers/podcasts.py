# This file is a part of MediaDrop (http://www.mediadrop.net),
# Copyright 2009-2013 MediaDrop contributors
# For the exact contribution history, see the git revision log.
# The source code contained in this file is licensed under the GPLv3 or
# (at your option) any later version.
# See LICENSE.txt in the main project directory, for more information.

from pylons import request, response
from sqlalchemy import orm

from mediacore.lib.auth.util import viewable_media
from mediacore.lib import helpers
from mediacore.lib.base import BaseController
from mediacore.lib.decorators import (beaker_cache, expose, observable, 
    paginate, validate)
from mediacore.lib.helpers import content_type_for_response, url_for, redirect
from mediacore.model import Media, Podcast, fetch_row
from mediacore.plugin import events
from mediacore.validation import LimitFeedItemsValidator

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
    def index(self, **kwargs):
        """List podcasts and podcast media.

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
            episode_query = podcast.media.published().order_by(Media.publish_on.desc())
            podcast_episodes[podcast] = viewable_media(episode_query)[:4]

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

        episodes = viewable_media(episodes)
        
        if request.settings['rss_display'] == 'True':
            response.feed_links.append(
               (url_for(action='feed'), podcast.title)
            )

        return dict(
            podcast = podcast,
            episodes = episodes,
            result_count = episodes.count(),
            show = show,
        )

    @validate(validators={'limit': LimitFeedItemsValidator()})
    @beaker_cache(expire=60 * 20)
    @expose('podcasts/feed.xml')
    @observable(events.PodcastsController.feed)
    def feed(self, slug, limit=None, **kwargs):
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

        response.content_type = content_type_for_response(
            ['application/rss+xml', 'application/xml', 'text/xml'])

        episode_query = podcast.media.published().order_by(Media.publish_on.desc())
        episodes = viewable_media(episode_query)
        if limit is not None:
            episodes = episodes.limit(limit)

        return dict(
            podcast = podcast,
            episodes = episodes,
        )
