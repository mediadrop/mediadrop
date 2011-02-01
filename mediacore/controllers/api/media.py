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

import logging
from datetime import datetime, timedelta

from paste.util.converters import asbool
from pylons import app_globals, config, request, response, session, tmpl_context
from sqlalchemy import orm, sql

from mediacore.controllers.api import APIException, get_order_by
from mediacore.lib import helpers
from mediacore.lib.base import BaseController
from mediacore.lib.decorators import expose, expose_xhr, observable, paginate, validate
from mediacore.lib.helpers import get_featured_category, url_for
from mediacore.lib.thumbnails import thumb
from mediacore.model import Category, Media, Podcast, Tag, fetch_row, get_available_slug
from mediacore.model.meta import DBSession
from mediacore.plugin import events

log = logging.getLogger(__name__)

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

AUTHERROR = "Authentication Error"
INVALIDFORMATERROR = "Invalid format (%s). Only json and mrss are supported"

class MediaController(BaseController):
    """
    JSON Media API
    """

    @expose('json')
    @observable(events.API.MediaController.index)
    def index(self, type=None, podcast=None, tag=None, category=None, search=None,
              max_age=None, min_age=None, order=None, offset=0, limit=10,
              published_after=None, published_before=None, featured=False,
              id=None, slug=None, include_embed=False, api_key=None, format="json", **kwargs):
        """Query for a list of media.

        :param type:
            Filter by 'audio' or 'video'. Defaults to any type.

        :param podcast:
            A podcast slug (or slugs) to filter by. Use 0 to include
            only non-podcast media or 1 to include any podcast media.
            For multiple podcasts, separate the slugs with commas.

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
            :attr:`app_globals.settings['api_media_max_results']`.
        :type limit: int

        :param featured:
            If nonzero, the results will only include media from the
            configured featured category, if there is one.
        :type featured: bool

        :param include_embed:
            If nonzero, the HTML for the embeddable player is included
            for all results.
        :type include_embed: bool

        :param id:
            Filters the results to include the one item with the given ID.
            Note that we still return a list.
        :type id: int or None

        :param slug:
            Filters the results to include the one item with the given slug.
            Note that we still return a list.
        :type slug: unicode or None

        :param api_key:
            The api access key if required in settings
        :type api_key: unicode or None

        :raises APIException:
            If there is an user error in the query params.

        :rtype: JSON dict
        :returns:
            count
                The total number of results that match this query.
            media
                A list of media info objects.

        """

        if asbool(app_globals.settings['api_secret_key_required']) \
            and api_key != app_globals.settings['api_secret_key']:
            return dict(error=AUTHERROR)

        if format not in ("json", "mrss"):
            return dict(error= INVALIDFORMATERROR % format)

        query = Media.query\
            .published()\
            .options(orm.undefer('comment_count_published'))

        # Basic filters
        if id:
            query = query.filter_by(id=id)
        if slug:
            query = query.filter_by(slug=slug)

        if type:
            query = query.filter_by(type=type)

        if podcast:
            podcast_query = DBSession.query(Podcast.id)\
                .filter(Podcast.slug.in_(podcast.split(',')))
            query = query.filter(Media.podcast_id.in_(podcast_query))

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

        query = query.order_by(get_order_by(order, order_columns))

        # Search will supercede the ordering above
        if search:
            query = query.search(search)

        if featured:
            featured_cat = get_featured_category()
            if featured_cat:
                query = query.in_category(featured_cat)

        # Preload podcast slugs so we don't do n+1 queries
        podcast_slugs = dict(DBSession.query(Podcast.id, Podcast.slug))

        # Rudimentary pagination support
        start = int(offset)
        end = start + min(int(limit), int(app_globals.settings['api_media_max_results']))

        if format == "mrss":
            request.override_template = "sitemaps/mrss.xml"
            return dict(
                media = query[start:end],
                title = "Media Feed",
            )

        media = [self._info(m, podcast_slugs, include_embed) for m in query[start:end]]

        return dict(
            media = media,
            count = query.count(),
        )


    @expose('json')
    @observable(events.API.MediaController.get)
    def get(self, id=None, slug=None, api_key=None, format="json", **kwargs):
        """Expose info on a specific media item by ID or slug.

        :param id: A :attr:`mediacore.model.media.Media.id` for lookup
        :type id: int
        :param slug: A :attr:`mediacore.model.media.Media.slug` for lookup
        :type slug: str
        :param api_key:
            The api access key if required in settings
        :type api_key: unicode or None
        :raises webob.exc.HTTPNotFound: If the media doesn't exist.
        :returns: JSON dict

        """
        if asbool(app_globals.settings['api_secret_key_required']) \
            and api_key != app_globals.settings['api_secret_key']:
            return dict(error=AUTHERROR)

        if format not in ("json", "mrss"):
            return dict(error= INVALIDFORMATERROR % format)

        query = Media.query.published()

        if id:
            query = query.filter_by(id=id)
        else:
            query = query.filter_by(slug=slug)

        try:
            media = query.one()
        except orm.exc.NoResultFound:
            return dict(error="No match found")

        if format == "mrss":
            request.override_template = "sitemaps/mrss.xml"
            return dict(
                media = [media],
                title = "Media Entry",
            )

        return self._info(media, include_embed=True)


    def _info(self, media, podcast_slugs=None, include_embed=False):
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
            thumbs[size] = thumb(media, size, qualified=True)

        info = dict(
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
            publish_on = unicode(media.publish_on),
            likes = media.likes,
            views = media.views,
            thumbs = thumbs,
            categories = dict((c.slug, c.name) for c in list(media.categories)),
        )

        if include_embed:
            info['embed'] = unicode(helpers.embed_player(media))

        return info


    @expose('json')
    def files(self, id=None, slug=None, api_key=None, **kwargs):
        """List all files related to specific media.

        :param id: A :attr:`mediacore.model.media.Media.id` for lookup
        :type id: int
        :param slug: A :attr:`mediacore.model.media.Media.slug` for lookup
        :type slug: str
        :param api_key:
            The api access key if required in settings
        :type api_key: unicode or None
        :raises webob.exc.HTTPNotFound: If the media doesn't exist.
        :returns: JSON dict

        """
        if asbool(app_globals.settings['api_secret_key_required']) \
            and api_key != app_globals.settings['api_secret_key']:
            return dict(error='Authentication Error')

        query = Media.query.published()

        if id:
            query = query.filter_by(id=id)
        else:
            query = query.filter_by(slug=slug)

        try:
            media = query.one()
        except orm.exc.NoResultFound:
            return dict(error='No match found')

        return dict(
            files = [self._file_info(f, media) for f in media.files],
        )

    def _file_info(self, file, media):
        """Return a JSON-ready dict for the media file including links."""
        uris = []
        info = dict(
            container = file.container,
            type = file.type,
            display_name = file.display_name,
            created = file.created_on.isoformat(),
            link = helpers.url_for(controller='/media', action='view',
                                   slug=media.slug, qualified=True),
            uris = uris,
        )
        for uri in file.get_uris():
            uris.append({
                'scheme': uri.scheme,
                'uri': str(uri),
                'server_uri': uri.server_uri,
                'file_uri': uri.file_uri,
            })
        return info
