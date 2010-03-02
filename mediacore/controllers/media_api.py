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
import simplejson as json
import time
from urlparse import urlparse
from datetime import datetime, timedelta, date

from tg import config, request, response, tmpl_context
import tg.exceptions
from sqlalchemy import orm, sql

from mediacore.lib.base import (BaseController, url_for, redirect,
    expose, expose_xhr, validate, paginate)
from mediacore.model import (DBSession, fetch_row, get_available_slug,
    Media, Tag, Topic, Podcast)
from mediacore.lib import helpers

class APIUserException(Exception):
    """
    API Usage Error -- wrapper for providing helpful error messages.
    TODO: Actually display these messages!!
    """

order_columns = {
    'id': Media.id,
    'slug': Media.slug,
    'type': Media.type,
    'publish_on': Media.publish_on,
    'duration': Media.duration,
    'views': Media.views,
    'likes': Media.likes,
    'description': Media.description,
    'description_plain': Media.description_plain,
    'comment_count': 'comment_count_published %s'
}

class MediaApiController(BaseController):
    """Media actions -- for both regular and podcast media"""

    @expose('json')
    def index(self, type=None, podcast=None, tag=None, topic=None, search=None,
              order=None, offset=0, per_page=10, **kwargs):
        """Query the media list.

        :param type: 'audio' or 'video'. Defaults to any type.
        :param order: A column name and 'asc' or 'desc', seperated by a
            space. The column name can be any one of the returned columns.
            Defaults to newest media first (publish_on desc).
        :param search: A boolean search query. See
            http://dev.mysql.com/doc/refman/5.0/en/fulltext-boolean.html
        :param podcast: A podcast slug to filter by. Use 0 to include
            only non-podcast media.
        :param tag: A tag slug to filter by.
        :param topic: A topic slug to filter by.
        :param offset: Where in the resultset to start when returning results.
            Defaults to 0, the very beginning.
        :type offset: int
        :param per_page: Number of results to return in each query.
            Defaults to 10. The maximum allowed value is set in
            :attr:`mediacore.config.app_config.api_max_results`,
            which is 20 by default.
        :type per_page: int
        :returns: JSON dict

        """
        query = Media.query.published()\
            .options(orm.undefer('comment_count_published'))

        # Basic filters
        if type:
            query = query.filter_by(type=type)

        if podcast:
            podcast_query = DBSession.query(Podcast.id).filter_by(slug=podcast)
            query = query.filter_by(podcast_id=podcast_query.scalar())

        if tag:
            tag = fetch_row(Tag, slug=tag)
            query = query.filter(Media.tags.contains(tag))

        if topic:
            topic = fetch_row(Topic, slug=topic)
            query = query.filter(Media.topics.contains(topic))

        # Split the order into two parts, column and direction
        if not order:
            order_col, order_dir = 'publish_on', 'desc'
        else:
            try:
                order_col, order_dir = unicode(order).strip().lower().split(' ')
                assert order_dir in ('asc', 'desc')
            except:
                raise APIException, 'Invalid order format, must be "column asc/desc", given "%s"' % order

        # Get the order clause for the given column name
        try:
            order_attr = order_columns[order_col]
        except KeyError:
            raise APIException, 'Not allowed to order by "%s", please pick one of %s' % (order_col, ', '.join(order_columns.keys()))

        # Normalize to something that can be used in a query
        if isinstance(order_attr, basestring):
            order = sql.text(order_attr % ('asc' if order_dir == 'asc' else 'desc'))
        else:
            # Assume this is an sqlalchemy InstrumentedAttribute
            order = getattr(order_attr, order_dir)()
        query = query.order_by(order)

        # Search will supercede the ordering above
        if search:
            query = query.search(search)

        # Preload podcast slugs so we don't do n+1 queries
        podcast_slugs = dict(DBSession.query(Podcast.id, Podcast.slug))

        # Rudimentary pagination support
        start = int(offset)
        end = start + min(int(per_page), int(config.api_media_max_results))

        media = [self._info(m, podcast_slugs) for m in query[start:end]]

        return dict(
            media = media,
            count = query.count()
        )


    @expose('json')
    def get(self, id=None, slug=None, **kwargs):
        """Expose info on a specific media item, found by ID or slug.

        :param id: A :attr:`mediacore.model.media.Media.slug` for lookup
        :type id: int
        :param slug: A :attr:`mediacore.model.media.Media.slug` for lookup
        :type slug: str
        :raises tg.exceptions.HTTPNotFound: If the media doesn't exist.
        :returns: JSON dict

        """
        query = Media.query.published()

        if id:
            query = query.filter_by(id=id)
        else:
            query = query.filter_by(slug=slug)

        try:
            media = query.one()
        except orm.exc.NoResultFound:
            raise tg.exceptions.HTTPNotFound

        info = self._info(media)
        info['embed'] = helpers.embeddable_player(media)
        return info


    def _info(self, media, podcast_slugs=None):
        """Return a JSON-ready dict for the given media instance"""
        if media.podcast_id:
            media_url = url_for(controller='/media', action='view', slug=media.slug,
                                podcast_slug=media.podcast.slug, qualified=True)
        else:
            media_url = url_for(controller="/media", action="view", slug=media.slug,
                                qualified=True)

        if media.podcast_id is None:
            podcast_slug = None
        elif podcast_slugs:
            podcast_slug = podcast_slugs[media.podcast_id]
        else:
            podcast_slug = DBSession.query(Podcast.slug)\
                .filter_by(id=media.podcast_id).scalar()

        thumbs = {}
        for size in config.thumb_sizes[media._thumb_dir].iterkeys():
            thumbs[size] = helpers.thumb(media, size, qualified=True)

        return dict(
            id = media.id,
            slug = media.slug,
            url = media_url,
            title = media.title,
            type = media.type,
            podcast = podcast_slug,
            description = media.description,
            description_plain = media.description_plain,
            comment_count = media.comment_count_published,
            likes = media.likes,
            views = media.views,
            thumbs = thumbs,
        )
