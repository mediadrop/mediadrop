# This file is a part of MediaDrop (http://www.mediadrop.net),
# Copyright 2009-2013 MediaDrop contributors
# For the exact contribution history, see the git revision log.
# The source code contained in this file is licensed under the GPLv3 or
# (at your option) any later version.
# See LICENSE.txt in the main project directory, for more information.

"""
Sitemaps Controller
"""
import logging
import math
import os

from formencode import validators
from paste.fileapp import FileApp
from pylons import config, request, response
from pylons.controllers.util import abort, forward
from webob.exc import HTTPNotFound

from mediadrop.plugin import events
from mediadrop.lib.base import BaseController
from mediadrop.lib.decorators import expose, beaker_cache, observable, validate
from mediadrop.lib.helpers import (content_type_for_response, 
    get_featured_category, url_for, viewable_media)
from mediadrop.model import Media
from mediadrop.validation import LimitFeedItemsValidator

log = logging.getLogger(__name__)

# Global cache of the FileApp used to serve the crossdomain.xml file
# when static_files is disabled and no Apache alias is configured.
crossdomain_app = None


class SitemapsController(BaseController):
    """
    Sitemap generation
    """

    @validate(validators={
        'page': validators.Int(if_empty=None, if_missing=None, if_invalid=None), 
        'limit': validators.Int(if_empty=10000, if_missing=10000, if_invalid=10000)
    })
    @beaker_cache(expire=60 * 60 * 4)
    @expose('sitemaps/google.xml')
    @observable(events.SitemapsController.google)
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
            content_type_for_response(['application/xml', 'text/xml'])

        media = viewable_media(Media.query.published())

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
    @observable(events.SitemapsController.mrss)
    def mrss(self, **kwargs):
        """Generate a media rss (mRSS) feed of all the sites media."""
        if request.settings['sitemaps_display'] != 'True':
            abort(404)


        response.content_type = content_type_for_response(
            ['application/rss+xml', 'application/xml', 'text/xml'])

        media = viewable_media(Media.query.published())

        return dict(
            media = media,
            title = 'MediaRSS Sitemap',
        )

    @validate(validators={
        'limit': LimitFeedItemsValidator(),
        'skip': validators.Int(if_empty=0, if_missing=0, if_invalid=0)
    })
    @beaker_cache(expire=60 * 3)
    @expose('sitemaps/mrss.xml')
    @observable(events.SitemapsController.latest)
    def latest(self, limit=None, skip=0, **kwargs):
        """Generate a media rss (mRSS) feed of all the sites media."""
        if request.settings['rss_display'] != 'True':
            abort(404)

        response.content_type = content_type_for_response(
            ['application/rss+xml', 'application/xml', 'text/xml'])

        media_query = Media.query.published().order_by(Media.publish_on.desc())
        media = viewable_media(media_query)
        if limit is not None:
            media = media.limit(limit)

        if skip > 0:
            media = media.offset(skip)

        return dict(
            media = media,
            title = 'Latest Media',
        )

    @validate(validators={
        'limit': LimitFeedItemsValidator(),
        'skip': validators.Int(if_empty=0, if_missing=0, if_invalid=0)
    })
    @beaker_cache(expire=60 * 3)
    @expose('sitemaps/mrss.xml')
    @observable(events.SitemapsController.featured)
    def featured(self, limit=None, skip=0, **kwargs):
        """Generate a media rss (mRSS) feed of the sites featured media."""
        if request.settings['rss_display'] != 'True':
            abort(404)

        response.content_type = content_type_for_response(
            ['application/rss+xml', 'application/xml', 'text/xml'])

        media_query = Media.query.in_category(get_featured_category())\
            .published()\
            .order_by(Media.publish_on.desc())
        media = viewable_media(media_query)
        if limit is not None:
            media = media.limit(limit)

        if skip > 0:
            media = media.offset(skip)

        return dict(
            media = media,
            title = 'Featured Media',
        )

    @expose()
    def crossdomain_xml(self, **kwargs):
        """Serve the crossdomain XML file manually if static_files is disabled.

        If someone forgets to add this Alias we might as well serve this file
        for them and save everyone the trouble. This only works when MediaDrop
        is served out of the root of a domain and if Cooliris is enabled.
        """
        global crossdomain_app

        if not request.settings['appearance_enable_cooliris']:
            # Ensure the cache is cleared if cooliris is suddenly disabled
            if crossdomain_app:
                crossdomain_app = None
            raise HTTPNotFound()

        if not crossdomain_app:
            relpath = 'mediadrop/public/crossdomain.xml'
            abspath = os.path.join(config['here'], relpath)
            crossdomain_app = FileApp(abspath)

        return forward(crossdomain_app)
