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
    
    index = google
    
    @expose('sitemaps/mrss.xml')
    def mrss(self, *args,  **kwargs):
        """ Generate a media rss (mRSS) feed of all the sites media """
        
        response.content_type = mimeparse.best_match(
            ['application/rss+xml', 'application/xml', 'text/xml'],
            request.environ.get('HTTP_ACCEPT', '*/*')
        )
        
        media = Media.query.published()\
            .options(orm.undefer('comment_count_published'))
            
        return dict(media=media)
        