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
Publicly Facing Media Controllers
"""
from pylons import app_globals, config, request, response, session, tmpl_context
import webob.exc
from sqlalchemy import orm, sql
from paste.deploy.converters import asbool
from paste.fileapp import FileApp
from paste.util import mimeparse
from akismet import Akismet

from mediacore.lib.base import BaseController
from mediacore.lib.decorators import expose, expose_xhr, paginate, validate
from mediacore.lib.helpers import url_for, redirect, store_transient_message
from mediacore.model import (DBSession, fetch_row, get_available_slug,
    Media, MediaFile, Comment, Tag, Category, Author, AuthorWithIP, Podcast)
from mediacore.lib import helpers, email
from mediacore import USER_AGENT

import logging
log = logging.getLogger(__name__)


class SitemapController(BaseController):
    """
    Sitemap generation
    """

    @expose('sitemaps/index.html')
    @paginate('media', items_per_page=20)
    def index(self, page=1, show='latest', q=None, tag=None, **kwargs):
        """List media with pagination.

        The media paginator may be accessed in the template with
        :attr:`c.paginators.media`, see :class:`webhelpers.paginate.Page`.

        :param page: Page number, defaults to 1.
        :type page: int
        :param show: 'latest', 'popular' or 'featured'
        :type show: unicode or None
        :param q: A search query to filter by
        :type q: unicode or None
        :param tag: A tag slug to filter for
        :type tag: unicode or None
        :rtype: dict
        :returns:
            media
                The list of :class:`~mediacore.model.media.Media` instances
                for this page.
            result_count
                The total number of media items for this query
            search_query
                The query the user searched for, if any

        """
        media = Media.query.published()\
            .options(orm.undefer('comment_count_published'))

        media, show = helpers.filter_library_controls(media, show)

        if q:
            media = media.search(q, bool=True)
        if tag:
            tag = fetch_row(Tag, slug=tag)
            media = media.filter(Media.tags.contains(tag))

        return dict(
            media = media,
            result_count = media.count(),
            search_query = q,
            show = show,
            tag = tag,
        )

    @expose('sitemaps/google.xml')
    def google(self, *args, **kwargs):
        """ Generate a google compatible Video Sitemap """
        
        #TODO:  check and handle sitemap size limits
        response.content_type = mimeparse.best_match(
            ['application/rss+xml', 'application/xml', 'text/xml'],
            request.environ.get('HTTP_ACCEPT', '*/*')
        )
        media = Media.query.published()\
            .options(orm.undefer('comment_count_published'))
            
        return dict(media=media)
    
    @expose('sitemaps/mrss.xml')
    def mrss(self, slug, **kwargs):
        return dict()
    
        