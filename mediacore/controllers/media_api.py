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


from datetime import datetime, timedelta
from pylons import config, request, response, session, tmpl_context
from sqlalchemy import orm, sql
import webob.exc

from mediacore.lib.base import BaseController
from mediacore.lib.decorators import expose, expose_xhr, paginate, validate
from mediacore.lib.helpers import url_for
from mediacore.lib import helpers
from mediacore.model import Category, Media, Podcast, Tag, fetch_row, get_available_slug
from mediacore.model.meta import DBSession

import logging
log = logging.getLogger(__name__)

class APIException(Exception):
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
    'popularity': Media.popularity_points,
    'description': Media.description,
    'description_plain': Media.description_plain,
    'comment_count': 'comment_count_published %s'
}

class MediaApiController(BaseController):
    """
    JSON Media API
    """

    @expose('json')
    def index(self, type=None, podcast=None, tag=None, category=None, search=None,
              max_age=None, min_age=None, order=None, offset=0, limit=10,
              published_after=None, published_before=None, **kwargs):
        """Query for a list of media.

        :param type:
            Filter by 'audio' or 'video'. Defaults to any type.

        :param podcast:
            A podcast slug to filter by. Use 0 to include
            only non-podcast media or 1 to include any podcast media.

        :param tag:
            A tag slug to filter by.

        :param category:
            A category slug to filter by.

        :param search:
            A boolean search query. See
            http://dev.mysql.com/doc/refman/5.0/en/fulltext-boolean.html

        :param published_after:
            If given, only media published *on or after* this date is
            returned. The expected format is 'YYYY-MM-DD HH:MM:SS' and
            must include the year at a bare minimum.

        :param published_before:
            If given, only media published *on or before* this date is
            returned. The expected format is 'YYYY-MM-DD HH:MM:SS' and
            must include the year at a bare minimum.

        :param max_age:
            If given, only media published within this many days is
            returned. This is a convenience shortcut for publish_after
            and will override its value if both are given.
        :type max_age: int

        :param min_age:
            If given, only media published prior to this number of days
            ago will be returned. This is a convenience shortcut for
            publish_before and will override its value if both are given.
        :type min_age: int

        :param order:
            A column name and 'asc' or 'desc', seperated by a space.
            The column name can be any one of the returned columns.
            Defaults to newest media first (publish_on desc).

        :param offset:
            Where in the complete resultset to start returning results.
            Defaults to 0, the very beginning. This is useful if you've
            already fetched the first 50 results and want to fetch the
            next 50 and so on.
        :type offset: int

        :param limit:
            Number of results to return in each query. Defaults to 10.
            The maximum allowed value defaults to 50 and is set via
            :attr:`mediacore.config['app_config'].api_media_max_results`.
        :type limit: int

        :raises APIException:
            If there is an user error in the query params.

        :rtype: JSON dict
        :returns:
            count
                The total number of results that match this query.
            media
                A list of media info objects.

        """
        query = Media.query\
            .published()\
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

        if category:
            category = fetch_row(Category, slug=category)
            query = query.filter(Media.categories.contains(category))

        if max_age:
            published_after = datetime.now() - timedelta(days=int(max_age))
        if min_age:
            published_before = datetime.now() - timedelta(days=int(min_age))

        # FIXME: Parse the date and catch formatting problems before it
        #        it hits the database. Right now support for partial
        #        dates like '2010-02' is thanks to leniancy in MySQL.
        #        Hopefully this leniancy is common to Postgres etc.
        if published_after:
            query = query.filter(Media.publish_on >= published_after)
        if published_before:
            query = query.filter(Media.publish_on <= published_before)

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
            order = sql.text(order_attr % (order_dir == 'asc' and 'asc' or 'desc'))
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
        end = start + min(int(limit), int(config['api_media_max_results']))

        media = [self._info(m, podcast_slugs) for m in query[start:end]]

        return dict(
            media = media,
            count = query.count()
        )


    @expose('json')
    def get(self, id=None, slug=None, **kwargs):
        """Expose info on a specific media item by ID or slug.

        :param id: A :attr:`mediacore.model.media.Media.id` for lookup
        :type id: int
        :param slug: A :attr:`mediacore.model.media.Media.slug` for lookup
        :type slug: str
        :raises webob.exc.HTTPNotFound: If the media doesn't exist.
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
            raise webob.exc.HTTPNotFound

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
        for size in config['thumb_sizes'][media._thumb_dir].iterkeys():
            thumbs[size] = helpers.thumb(media, size, qualified=True)

        return dict(
            id = media.id,
            slug = media.slug,
            url = media_url,
            title = media.title,
            author = media.author.name,
            type = media.type,
            podcast = podcast_slug,
            description = media.description,
            description_plain = media.description_plain,
            comment_count = media.comment_count_published,
            publish_on = media.publish_on,
            likes = media.likes,
            views = media.views,
            thumbs = thumbs,
            topics = dict((t.slug, t.name) for t in list(media.topics)),
        )
