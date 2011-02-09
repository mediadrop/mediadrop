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

"""
Sitemaps Controller
"""
import logging
import math

from paste.util import mimeparse
from pylons import app_globals, request, response
from pylons.controllers.util import abort

from mediacore.lib.base import BaseController
from mediacore.lib.decorators import expose, beaker_cache
from mediacore.lib.helpers import get_featured_category, redirect, url_for
from mediacore.model import Media

log = logging.getLogger(__name__)

class SitemapsController(BaseController):
    """
    Sitemap generation
    """

    @beaker_cache(expire=60 * 60 * 4, query_args=True)
    @expose('sitemaps/google.xml')
    def google(self, page=None, limit=10000, **kwargs):
        """Generate a sitemap which contains googles Video Sitemap information.

        This action may return a <sitemapindex> or a <urlset>, depending
        on how many media items are in the database, and the values of the
        page and limit params.

        :param page: Page number, defaults to 1.
        :type page: int
        :param page: max records to display on page, defaults to 10000.
        :type page: int

        """
        if app_globals.settings['sitemaps_display'] != 'True':
            abort(404)

        response.content_type = mimeparse.best_match(
            ['application/xml', 'text/xml'],
            request.environ.get('HTTP_ACCEPT', '*/*')
        )

        media = Media.query.published()

        if page is None:
            if media.count() > limit:
                return dict(pages=math.ceil(media.count() / float(limit)))
        else:
            page = int(page)
            media = media.offset(page * limit).limit(limit)

        if page:
            links = []
        else:
            links = [
                url_for(controller='/', qualified=True),
                url_for(controller='/media', show='poplular', qualified=True),
                url_for(controller='/media', show='latest', qualified=True),
                url_for(controller='/categories', qualified=True),
            ]

        return dict(
            media = media,
            page = page,
            links = links,
        )

    @beaker_cache(expire=60 * 60, query_args=True)
    @expose('sitemaps/mrss.xml')
    def mrss(self, **kwargs):
        """Generate a media rss (mRSS) feed of all the sites media."""
        if app_globals.settings['sitemaps_display'] != 'True':
            abort(404)

        response.content_type = mimeparse.best_match(
            ['application/rss+xml', 'application/xml', 'text/xml'],
            request.environ.get('HTTP_ACCEPT', '*/*')
        )

        media = Media.query.published()

        return dict(
            media = media,
            title = 'MediaRSS Sitemap',
        )

    @beaker_cache(expire=60 * 3, query_args=True)
    @expose('sitemaps/mrss.xml')
    def latest(self, limit=30, skip=0, **kwargs):
        """Generate a media rss (mRSS) feed of all the sites media."""
        if app_globals.settings['rss_display'] != 'True':
            abort(404)

        response.content_type = mimeparse.best_match(
            ['application/rss+xml', 'application/xml', 'text/xml'],
            request.environ.get('HTTP_ACCEPT', '*/*')
        )

        media = Media.query.published()\
            .order_by(Media.publish_on.desc())\
            .limit(limit)

        if skip > 0:
            media = media.offset(skip)

        return dict(
            media = media,
            title = 'Latest Media',
        )

    @beaker_cache(expire=60 * 3, query_args=True)
    @expose('sitemaps/mrss.xml')
    def featured(self, limit=30, skip=0, **kwargs):
        """Generate a media rss (mRSS) feed of the sites featured media."""
        if app_globals.settings['rss_display'] != 'True':
            abort(404)

        response.content_type = mimeparse.best_match(
            ['application/rss+xml', 'application/xml', 'text/xml'],
            request.environ.get('HTTP_ACCEPT', '*/*')
        )

        media = Media.query.in_category(get_featured_category())\
            .order_by(Media.publish_on.desc())\
            .limit(limit)

        if skip > 0:
            media = media.offset(skip)

        return dict(
            media = media,
            title = 'Featured Media',
        )
