# This file is a part of MediaCore CE (http://www.mediacorecommunity.org),
# Copyright 2009-2013 MediaCore Inc., Felix Schwarz and other contributors.
# For the exact contribution history, see the git revision log.
# The source code contained in this file is licensed under the GPLv3 or
# (at your option) any later version.
# See LICENSE.txt in the main project directory, for more information.

"""
Publicly Facing Media Controllers
"""
import logging
import os.path

from akismet import Akismet
from paste.fileapp import FileApp
from paste.util import mimeparse
from pylons import config, request, response
from pylons.controllers.util import abort, forward
from sqlalchemy import orm, sql
from sqlalchemy.exc import OperationalError
from webob.exc import HTTPNotAcceptable, HTTPNotFound

from mediacore import USER_AGENT
from mediacore.forms.comments import PostCommentSchema
from mediacore.lib import helpers
from mediacore.lib.base import BaseController
from mediacore.lib.decorators import expose, expose_xhr, observable, paginate, validate_xhr, autocommit
from mediacore.lib.email import send_comment_notification
from mediacore.lib.helpers import (filter_vulgarity, redirect, url_for, 
    viewable_media)
from mediacore.lib.i18n import _
from mediacore.lib.services import Facebook
from mediacore.lib.templating import render
from mediacore.model import (DBSession, fetch_row, Media, MediaFile, Comment, 
    Tag, Category, AuthorWithIP, Podcast)
from mediacore.plugin import events

log = logging.getLogger(__name__)

comment_schema = PostCommentSchema()

class MediaController(BaseController):
    """
    Media actions -- for both regular and podcast media
    """

    @expose('media/index.html')
    @paginate('media', items_per_page=10)
    @observable(events.MediaController.index)
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
        media = Media.query.published()

        media, show = helpers.filter_library_controls(media, show)

        if q:
            media = media.search(q, bool=True)

        if tag:
            tag = fetch_row(Tag, slug=tag)
            media = media.filter(Media.tags.contains(tag))

        media = viewable_media(media)
        return dict(
            media = media,
            result_count = media.count(),
            search_query = q,
            show = show,
            tag = tag,
        )

    @expose('media/tags.html')
    def tags(self, **kwargs):
        """Display a listing of all tags."""
        tags = Tag.query\
            .options(orm.undefer('media_count_published'))\
            .filter(Tag.media_count_published > 0)
        return dict(
            tags = tags,
        )

    @expose('media/explore.html')
    @observable(events.MediaController.explore)
    def explore(self, **kwargs):
        """Display the most recent 15 media.

        :rtype: Dict
        :returns:
            latest
                Latest media
            popular
                Latest media

        """
        media = Media.query.published()

        latest = media.order_by(Media.publish_on.desc())
        popular = media.order_by(Media.popularity_points.desc())

        featured = None
        featured_cat = helpers.get_featured_category()
        if featured_cat:
            featured = viewable_media(latest.in_category(featured_cat)).first()
        if not featured:
            featured = viewable_media(popular).first()

        latest = viewable_media(latest.exclude(featured))[:8]
        popular = viewable_media(popular.exclude(featured, latest))[:5]
        if request.settings['sitemaps_display'] == 'True':
            response.feed_links.extend([
                (url_for(controller='/sitemaps', action='google'), u'Sitemap XML'),
                (url_for(controller='/sitemaps', action='mrss'), u'Sitemap RSS'),
            ])
        if request.settings['rss_display'] == 'True':
            response.feed_links.extend([
                (url_for(controller='/sitemaps', action='latest'), u'Latest RSS'),
            ])

        return dict(
            featured = featured,
            latest = latest,
            popular = popular,
            categories = Category.query.populated_tree(),
        )

    @expose()
    def random(self, **kwargs):
        """Redirect to a randomly selected media item."""
        # TODO: Implement something more efficient than ORDER BY RAND().
        #       This method does a full table scan every time.
        random_query = Media.query.published().order_by(sql.func.random())
        media = viewable_media(random_query).first()

        if media is None:
            redirect(action='explore')
        if media.podcast_id:
            podcast_slug = DBSession.query(Podcast.slug).get(media.podcast_id)
        else:
            podcast_slug = None
        redirect(action='view', slug=media.slug, podcast_slug=podcast_slug)

    @expose('media/view.html')
    @observable(events.MediaController.view)
    def view(self, slug, podcast_slug=None, **kwargs):
        """Display the media player, info and comments.

        :param slug: The :attr:`~mediacore.models.media.Media.slug` to lookup
        :param podcast_slug: The :attr:`~mediacore.models.podcasts.Podcast.slug`
            for podcast this media belongs to. Although not necessary for
            looking up the media, it tells us that the podcast slug was
            specified in the URL and therefore we reached this action by the
            preferred route.
        :rtype dict:
        :returns:
            media
                The :class:`~mediacore.model.media.Media` instance for display.
            related_media
                A list of :class:`~mediacore.model.media.Media` instances that
                rank as topically related to the given media item.
            comments
                A list of :class:`~mediacore.model.comments.Comment` instances
                associated with the selected media item.
            comment_form_action
                ``str`` comment form action
            comment_form_values
                ``dict`` form values
            next_episode
                The next episode in the podcast series, if this media belongs to
                a podcast, another :class:`~mediacore.model.media.Media`
                instance.

        """
        media = fetch_row(Media, slug=slug)
        request.perm.assert_permission(u'view', media.resource)

        if media.podcast_id is not None:
            # Always view podcast media from a URL that shows the context of the podcast
            if url_for() != url_for(podcast_slug=media.podcast.slug):
                redirect(podcast_slug=media.podcast.slug)

        try:
            media.increment_views()
            DBSession.commit()
        except OperationalError:
            DBSession.rollback()

        if request.settings['comments_engine'] == 'facebook':
            response.facebook = Facebook(request.settings['facebook_appid'])

        related_media = viewable_media(Media.query.related(media))[:6]
        # TODO: finish implementation of different 'likes' buttons
        #       e.g. the default one, plus a setting to use facebook.
        return dict(
            media = media,
            related_media = related_media,
            comments = media.comments.published().all(),
            comment_form_action = url_for(action='comment'),
            comment_form_values = kwargs,
        )

    @expose('players/iframe.html')
    @observable(events.MediaController.embed_player)
    def embed_player(self, slug, w=None, h=None, **kwargs):
        media = fetch_row(Media, slug=slug)
        request.perm.assert_permission(u'view', media.resource)
        return dict(
            media = media,
            width = w and int(w) or None,
            height = h and int(h) or None,
        )

    @expose(request_method="POST")
    @autocommit
    @observable(events.MediaController.rate)
    def rate(self, slug, up=None, down=None, **kwargs):
        """Say 'I like this' for the given media.

        :param slug: The media :attr:`~mediacore.model.media.Media.slug`
        :rtype: unicode
        :returns:
            The new number of likes

        """
        media = fetch_row(Media, slug=slug)
        request.perm.assert_permission(u'view', media.resource)

        if up:
            if not request.settings['appearance_show_like']:
                abort(status_code=403)
            media.increment_likes()
        elif down:
            if not request.settings['appearance_show_dislike']:
                abort(status_code=403)
            media.increment_dislikes()

        if request.is_xhr:
            return u''
        else:
            redirect(action='view')

    @expose_xhr(request_method='POST')
    @validate_xhr(comment_schema, error_handler=view)
    @autocommit
    @observable(events.MediaController.comment)
    def comment(self, slug, name='', email=None, body='', **kwargs):
        """Post a comment from :class:`~mediacore.forms.comments.PostCommentForm`.

        :param slug: The media :attr:`~mediacore.model.media.Media.slug`
        :returns: Redirect to :meth:`view` page for media.

        """
        def result(success, message=None, comment=None):
            if request.is_xhr:
                result = dict(success=success, message=message)
                if comment:
                    result['comment'] = render('comments/_list.html',
                        {'comment_to_render': comment},
                        method='xhtml')
                return result
            elif success:
                return redirect(action='view')
            else:
                return self.view(slug, name=name, email=email, body=body,
                                 **kwargs)

        if request.settings['comments_engine'] != 'mediacore':
            abort(404)
        akismet_key = request.settings['akismet_key']
        if akismet_key:
            akismet = Akismet(agent=USER_AGENT)
            akismet.key = akismet_key
            akismet.blog_url = request.settings['akismet_url'] or \
                url_for('/', qualified=True)
            akismet.verify_key()
            data = {'comment_author': name.encode('utf-8'),
                    'user_ip': request.environ.get('REMOTE_ADDR'),
                    'user_agent': request.environ.get('HTTP_USER_AGENT', ''),
                    'referrer': request.environ.get('HTTP_REFERER',  'unknown'),
                    'HTTP_ACCEPT': request.environ.get('HTTP_ACCEPT')}

            if akismet.comment_check(body.encode('utf-8'), data):
                return result(False, _(u'Your comment has been rejected.'))

        media = fetch_row(Media, slug=slug)
        request.perm.assert_permission(u'view', media.resource)

        c = Comment()

        name = filter_vulgarity(name)
        c.author = AuthorWithIP(name, email, request.environ['REMOTE_ADDR'])
        c.subject = 'Re: %s' % media.title
        c.body = filter_vulgarity(body)

        require_review = request.settings['req_comment_approval']
        if not require_review:
            c.reviewed = True
            c.publishable = True

        media.comments.append(c)
        DBSession.flush()
        send_comment_notification(media, c)

        if require_review:
            message = _('Thank you for your comment! We will post it just as '
                        'soon as a moderator approves it.')
            return result(True, message=message)
        else:
            return result(True, comment=c)

    @expose()
    def serve(self, id, download=False, **kwargs):
        """Serve a :class:`~mediacore.model.media.MediaFile` binary.

        :param id: File ID
        :type id: ``int``
        :param bool download: If true, serve with an Content-Disposition that
            makes the file download to the users computer instead of playing
            in the browser.
        :raises webob.exc.HTTPNotFound: If no file exists with this ID.
        :raises webob.exc.HTTPNotAcceptable: If an Accept header field
            is present, and if the mimetype of the requested file doesn't
            match, then a 406 (not acceptable) response is returned.

        """
        file = fetch_row(MediaFile, id=id)
        request.perm.assert_permission(u'view', file.media.resource)

        file_type = file.mimetype.encode('utf-8')
        file_name = file.display_name.encode('utf-8')

        file_path = helpers.file_path(file)
        if file_path is None:
            log.warn('No path exists for requested media file: %r', file)
            raise HTTPNotFound().exception
        file_path = file_path.encode('utf-8')

        if not os.path.exists(file_path):
            log.warn('No such file or directory: %r', file_path)
            raise HTTPNotFound().exception

        # Ensure the request accepts files with this container
        accept = request.environ.get('HTTP_ACCEPT', '*/*')
        if not mimeparse.best_match([file_type], accept):
            raise HTTPNotAcceptable().exception # 406

        method = config.get('file_serve_method', None)
        headers = []

        # Serving files with this header breaks playback on iPhone
        if download:
            headers.append(('Content-Disposition',
                            'attachment; filename="%s"' % file_name))

        if method == 'apache_xsendfile':
            # Requires mod_xsendfile for Apache 2.x
            # XXX: Don't send Content-Length or Etag headers,
            #      Apache handles them for you.
            response.headers['X-Sendfile'] = file_path
            response.body = ''

        elif method == 'nginx_redirect':
            # Requires NGINX server configuration:
            # NGINX must have a location block configured that matches
            # the __mediacore_serve__ path below. It should also be
            # configured as an "internal" location to prevent people from
            # surfing directly to it.
            # For more information see: http://wiki.nginx.org/XSendfile
            redirect_filename = '/__mediacore_serve__/%s' % os.path.basename(file_path)
            response.headers['X-Accel-Redirect'] = redirect_filename


        else:
            app = FileApp(file_path, headers, content_type=file_type)
            return forward(app)

        response.headers['Content-Type'] = file_type
        for header, value in headers:
            response.headers[header] = value

        return None
