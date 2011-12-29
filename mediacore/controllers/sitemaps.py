# This file is a part of MediaCore CE, Copyright 2009-2012 MediaCore Inc.
# The source code contained in this file is licensed under the GPL.
# See LICENSE.txt in the main project directory, for more information.

"""
Sitemaps Controller
"""
import logging
import math
import os

from paste.fileapp import FileApp
from paste.util import mimeparse
from pylons import app_globals, config, request, response
from pylons.controllers.util import abort, forward
from webob.exc import HTTPNotFound

from mediacore.lib.base import BaseController
from mediacore.lib.decorators import expose, beaker_cache
from mediacore.lib.helpers import get_featured_category, redirect, url_for
from mediacore.model import Media

log = logging.getLogger(__name__)

# Global cache of the FileApp used to serve the crossdomain.xml file
# when static_files is disabled and no Apache alias is configured.
crossdomain_app = None

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
        if request.settings['sitemaps_display'] != 'True':
            abort(404)

        response.content_type = \
            self._content_type_for_response(['application/xml', 'text/xml'])

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
                url_for(controller='/media', show='popular', qualified=True),
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
        if request.settings['sitemaps_display'] != 'True':
            abort(404)


        response.content_type = self._content_type_for_response(
            ['application/rss+xml', 'application/xml', 'text/xml'])

        media = Media.query.published()

        return dict(
            media = media,
            title = 'MediaRSS Sitemap',
        )

    @beaker_cache(expire=60 * 3, query_args=True)
    @expose('sitemaps/mrss.xml')
    def latest(self, limit=30, skip=0, **kwargs):
        """Generate a media rss (mRSS) feed of all the sites media."""
        if request.settings['rss_display'] != 'True':
            abort(404)

        response.content_type = self._content_type_for_response(
            ['application/rss+xml', 'application/xml', 'text/xml'])

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
        if request.settings['rss_display'] != 'True':
            abort(404)

        response.content_type = self._content_type_for_response(
            ['application/rss+xml', 'application/xml', 'text/xml'])

        media = Media.query.in_category(get_featured_category())\
            .published()\
            .order_by(Media.publish_on.desc())\
            .limit(limit)

        if skip > 0:
            media = media.offset(skip)

        return dict(
            media = media,
            title = 'Featured Media',
        )
    
    def _content_type_for_response(self, available_formats):
        content_type = mimeparse.best_match(
            available_formats,
            request.environ.get('HTTP_ACCEPT', '*/*')
        )
        # force a content-type: if the user agent did not specify any acceptable
        # content types (e.g. just 'text/html' like some bots) we still need to
        # set a content type, otherwise the WebOb will generate an exception
        # AttributeError: You cannot access Response.unicode_body unless charset
        # is set if user agents can not deal with xml, well, not our problem - 
        # in the end they requested a 'sitemap.xml' (or something similar)
        return content_type or available_formats[0]

    @expose()
    def crossdomain_xml(self, **kwargs):
        """Serve the crossdomain XML file manually if static_files is disabled.

        If someone forgets to add this Alias we might as well serve this file
        for them and save everyone the trouble. This only works when MediaCore
        is served out of the root of a domain and if Cooliris is enabled.
        """
        global crossdomain_app

        if not request.settings['appearance_enable_cooliris']:
            # Ensure the cache is cleared if cooliris is suddenly disabled
            if crossdomain_app:
                crossdomain_app = None
            raise HTTPNotFound().exception

        if not crossdomain_app:
            relpath = 'mediacore/public/crossdomain.xml'
            abspath = os.path.join(config['here'], relpath)
            crossdomain_app = FileApp(abspath)

        return forward(crossdomain_app)
