# This file is a part of MediaCore, Copyright 2009 Simple Station Inc.
#
# MediaCore is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# MediaCore is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from tg import config, request, response, tmpl_context
from sqlalchemy import orm
from repoze.what.predicates import has_permission
from paste.util import mimeparse
import pylons.templating

from mediacore.lib.base import (BaseController, url_for, redirect,
    expose, expose_xhr, validate, paginate)
from mediacore.model import (DBSession, fetch_row,
    Podcast, Media, Topic)


class PodcastsController(BaseController):
    """Podcast actions -- episodes are handled in the MediaController"""

    def __init__(self, *args, **kwargs):
        """Populate the :obj:`pylons.tmpl_context`` with topics.

        Used by :data:`mediacore.templates.helpers` to render the
        topic index flyout slider.

        """
        super(PodcastsController, self).__init__(*args, **kwargs)
        tmpl_context.nav_topics = DBSession.query(Topic)\
            .options(orm.undefer('published_media_count'))\
            .filter(Topic.published_media_count >= 1)\
            .order_by(Topic.name)\
            .all()
        tmpl_context.nav_podcasts = DBSession.query(Podcast).all()
        tmpl_context.nav_search = url_for(controller='/media', action='search')


    @expose('mediacore.templates.podcasts.index')
    @paginate('episodes', items_per_page=12, items_first_page=7)
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
            episodes
                The list of :class:`~mediacore.model.media.Media` instances
                for this page.

        """
        podcasts = Podcast.query\
            .options(orm.undefer('published_media_count'))\
            .all()

        episodes = Media.query.published()\
            .filter(Media.podcast_id != None)\
            .order_by(Media.publish_on.desc())\
            .options(orm.undefer('comment_count_published'))

        return dict(
            podcasts = podcasts,
            episodes = episodes,
        )


    @expose('mediacore.templates.podcasts.view')
    @paginate('episodes', items_per_page=10)
    def view(self, slug, page=1, **kwargs):
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
        episodes = podcast.media.published()\
            .order_by(Media.publish_on.desc())

        return dict(
            podcast = podcast,
            episodes = episodes,
        )


    @expose()
    def feed(self, slug, **kwargs):
        """Serve the feed as RSS 2.0.

        If :attr:`~mediacore.model.podcasts.Podcast.feedburner_url` is
        specified for this podcast, we redirect there.

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
        episodes = podcast.media.published()\
            .order_by(Media.publish_on.desc())

        podcasts = Podcast.query\
            .options(orm.undefer('published_media_count'))\
            .all()

        return dict(
            podcast = podcast,
            episodes = episodes,
            podcasts = podcasts,
        )


    @expose()
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

        Renders: :data:`mediacore.templates.podcasts.feed` XML

        """
        podcast = fetch_row(Podcast, slug=slug)

        if (podcast.feedburner_url
            and not 'feedburner' in request.environ.get('HTTP_USER_AGENT').lower()
            and not kwargs.get('feedburner_bypass', False)):
            redirect(podcast.feedburner_url.encode('utf-8'))

        # Choose the most appropriate content_type for the client
        response.content_type = mimeparse.best_match(
            ['application/rss+xml', 'application/xml', 'text/xml'],
            request.environ.get('HTTP_ACCEPT', '*/*')
        )

        episodes = podcast.media.published()\
            .order_by(Media.publish_on.desc())[:25]
        template_vars = dict(
            podcast = podcast,
            episodes = episodes,
        )

        # Manually render XML from genshi since tg is didnt consider it
        template_finder = config['pylons.app_globals'].dotted_filename_finder
        template_name = template_finder.get_dotted_filename(
            'mediacore.templates.podcasts.feed',
            template_extension='.xml'
        )
        return pylons.templating.render_genshi(
            template_name,
            extra_vars=template_vars,
            method='xml'
        )
