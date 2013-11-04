# This file is a part of MediaDrop (http://www.mediadrop.net),
# Copyright 2009-2013 MediaDrop contributors
# For the exact contribution history, see the git revision log.
# The source code contained in this file is licensed under the GPLv3 or
# (at your option) any later version.
# See LICENSE.txt in the main project directory, for more information.

from pylons import request, response, tmpl_context as c
from pylons.controllers.util import abort
from sqlalchemy import orm

from mediadrop.lib.base import BaseController
from mediadrop.lib.decorators import (beaker_cache, expose, observable, 
    paginate, validate)
from mediadrop.lib.helpers import content_type_for_response, url_for, viewable_media
from mediadrop.lib.i18n import _
from mediadrop.model import Category, Media, fetch_row
from mediadrop.plugin import events
from mediadrop.validation import LimitFeedItemsValidator

import logging
log = logging.getLogger(__name__)

class CategoriesController(BaseController):
    """
    Categories Controller

    Handles the display of the category hierarchy, displaying the media
    associated with any given category and its descendants.

    """

    def __before__(self, *args, **kwargs):
        """Load all our category data before each request."""
        BaseController.__before__(self, *args, **kwargs)

        c.categories = Category.query\
            .order_by(Category.name)\
            .options(orm.undefer('media_count_published'))\
            .populated_tree()

        counts = dict((cat.id, cat.media_count_published)
                      for cat, depth in c.categories.traverse())
        c.category_counts = counts.copy()
        for cat, depth in c.categories.traverse():
            count = counts[cat.id]
            if count:
                for ancestor in cat.ancestors():
                    c.category_counts[ancestor.id] += count

        category_slug = request.environ['pylons.routes_dict'].get('slug', None)
        if category_slug:
            c.category = fetch_row(Category, slug=category_slug)
            c.breadcrumb = c.category.ancestors()
            c.breadcrumb.append(c.category)

    @expose('categories/index.html')
    @observable(events.CategoriesController.index)
    def index(self, slug=None, **kwargs):
        media = Media.query.published()

        if c.category:
            media = media.in_category(c.category)
            
            response.feed_links.append((
                url_for(controller='/categories', action='feed', slug=c.category.slug),
                _('Latest media in %s') % c.category.name
            ))

        latest = media.order_by(Media.publish_on.desc())
        popular = media.order_by(Media.popularity_points.desc())

        latest = viewable_media(latest)[:5]
        popular = viewable_media(popular.exclude(latest))[:5]

        return dict(
            latest = latest,
            popular = popular,
        )

    @expose('categories/more.html')
    @paginate('media', items_per_page=20)
    @observable(events.CategoriesController.more)
    def more(self, slug, order, page=1, **kwargs):
        media = Media.query.published()\
            .in_category(c.category)

        if order == 'latest':
            media = media.order_by(Media.publish_on.desc())
        else:
            media = media.order_by(Media.popularity_points.desc())

        return dict(
            media = viewable_media(media),
            order = order,
        )

    @validate(validators={'limit': LimitFeedItemsValidator()})
    @beaker_cache(expire=60 * 3, query_args=True)
    @expose('sitemaps/mrss.xml')
    @observable(events.CategoriesController.feed)
    def feed(self, limit=None, **kwargs):
        """ Generate a media rss feed of the latest media

        :param limit: the max number of results to return. Defaults to 30

        """
        if request.settings['rss_display'] != 'True':
            abort(404)

        response.content_type = content_type_for_response(
            ['application/rss+xml', 'application/xml', 'text/xml'])

        media = Media.query.published()

        if c.category:
            media = media.in_category(c.category)

        media_query = media.order_by(Media.publish_on.desc())
        media = viewable_media(media_query)
        if limit is not None:
            media = media.limit(limit)

        return dict(
            media = media,
            title = u'%s Media' % c.category.name,
        )
