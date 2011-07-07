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

import os
import shutil
import tw.forms.fields

from datetime import datetime

import gdata.youtube
import gdata.youtube.service
from gdata.service import RequestError

from cgi import FieldStorage
from babel.core import Locale
from formencode import Invalid
from PIL import Image
from pylons import app_globals, config, request, response, session, tmpl_context as c
from repoze.what.predicates import has_permission
from sqlalchemy import orm, sql

from mediacore.forms.admin.settings import (AdvertisingForm, AppearanceForm,
    APIForm, AnalyticsForm, CommentsForm, GeneralForm, ImportVideosForm,
    NotificationsForm, PopularityForm, SiteMapsForm, UploadForm)
from mediacore.lib.base import BaseSettingsController
from mediacore.lib.decorators import (autocommit, expose, expose_xhr,
    paginate, validate)
from mediacore.lib.helpers import filter_vulgarity, redirect, url_for
from mediacore.lib.i18n import LanguageError, Translator
from mediacore.lib.storage import add_new_media_file, StorageError, UnsuitableEngineError, YoutubeStorage
from mediacore.lib.templating import render
from mediacore.lib.thumbnails import create_default_thumbs_for, has_thumbs
from mediacore.lib.xhtml import clean_xhtml
from mediacore.model import (Author, Category, Comment, Media, MediaFile, MultiSetting,
    Setting, fetch_row, get_available_slug)
from mediacore.model.meta import DBSession
from mediacore.websetup import appearance_settings, generate_appearance_css

import logging
log = logging.getLogger(__name__)

notifications_form = NotificationsForm(
    action=url_for(controller='/admin/settings', action='notifications_save'))

comments_form = CommentsForm(
    action=url_for(controller='/admin/settings', action='comments_save'))

api_form = APIForm(
    action=url_for(controller='/admin/settings', action='save_api'))

popularity_form = PopularityForm(
    action=url_for(controller='/admin/settings', action='popularity_save'))

upload_form = UploadForm(
    action=url_for(controller='/admin/settings', action='upload_save'))

analytics_form = AnalyticsForm(
    action=url_for(controller='/admin/settings', action='analytics_save'))

general_form = GeneralForm(
    action=url_for(controller='/admin/settings', action='general_save'))

sitemaps_form = SiteMapsForm(
    action=url_for(controller='/admin/settings', action='sitemaps_save'))

appearance_form = AppearanceForm(
    action=url_for(controller='/admin/settings', action='appearance_save'))

advertising_form = AdvertisingForm(
    action=url_for(controller='/admin/settings', action='advertising_save'))

importvideos_form = ImportVideosForm(
    action=url_for(controller='/admin/settings', action='importvideos_save'))


class SettingsController(BaseSettingsController):
    """
    Dumb controller for display and saving basic settings forms.

    See :class:`mediacore.lib.base.BaseSettingsController` for more details.

    """
    @expose()
    def index(self, **kwargs):
        redirect(action='general')

    @expose('admin/settings/notifications.html')
    def notifications(self, **kwargs):
        return self._display(notifications_form, values=kwargs)

    @expose(request_method='POST')
    @validate(notifications_form, error_handler=notifications)
    @autocommit
    def notifications_save(self, **kwargs):
        """Save :class:`~mediacore.forms.admin.settings.NotificationsForm`."""
        return self._save(notifications_form, 'notifications', values=kwargs)

    @expose('admin/settings/comments.html')
    def comments(self, **kwargs):
        return self._display(comments_form, values=kwargs)

    @expose(request_method='POST')
    @validate(comments_form, error_handler=comments)
    @autocommit
    def comments_save(self, **kwargs):
        """Save :class:`~mediacore.forms.admin.settings.CommentsForm`."""
        old_vulgarity_filter = c.settings['vulgarity_filtered_words'].value

        self._save(comments_form, values=kwargs)

        # Run the filter now if it has changed
        if old_vulgarity_filter != c.settings['vulgarity_filtered_words'].value:
            for comment in DBSession.query(Comment):
                comment.body = filter_vulgarity(comment.body)

        redirect(action='comments')

    @expose('admin/settings/api.html')
    def api(self, **kwargs):
        return self._display(api_form, values=kwargs)

    @expose(request_method='POST')
    @validate(api_form, error_handler=comments)
    @autocommit
    def save_api(self, **kwargs):
        """Save :class:`~mediacore.forms.admin.settings.APIForm`."""
        return self._save(api_form, 'api', values=kwargs)

    @expose('admin/settings/popularity.html')
    def popularity(self, **kwargs):
        return self._display(popularity_form, values=kwargs)

    @expose(request_method='POST')
    @validate(popularity_form, error_handler=popularity)
    @autocommit
    def popularity_save(self, **kwargs):
        """Save :class:`~mediacore.forms.admin.settings.PopularityForm`.

        Updates the popularity for every media item based on the submitted
        values.
        """
        self._save(popularity_form, values=kwargs)
        for m in Media.query:
            m.update_popularity()
            DBSession.add(m)
        redirect(action='popularity')

    @expose('admin/settings/upload.html')
    def upload(self, **kwargs):
        return self._display(upload_form, values=kwargs)

    @expose(request_method='POST')
    @validate(upload_form, error_handler=upload)
    @autocommit
    def upload_save(self, **kwargs):
        """Save :class:`~mediacore.forms.admin.settings.UploadForm`."""
        return self._save(upload_form, 'upload', values=kwargs)

    @expose('admin/settings/analytics.html')
    def analytics(self, **kwargs):
        return self._display(analytics_form, values=kwargs)

    @expose(request_method='POST')
    @validate(analytics_form, error_handler=analytics)
    @autocommit
    def analytics_save(self, **kwargs):
        """Save :class:`~mediacore.forms.admin.settings.AnalyticsForm`."""
        return self._save(analytics_form, 'analytics', values=kwargs)

    @expose('admin/settings/general.html')
    def general(self, **kwargs):
        if not c.settings['primary_language'].value:
            kwargs.setdefault('general', {}).setdefault('primary_language', 'en')
        return self._display(general_form, values=kwargs)

    @expose(request_method='POST')
    @validate(general_form, error_handler=general)
    @autocommit
    def general_save(self, **kwargs):
        """Save :class:`~mediacore.forms.admin.settings.GeneralForm`."""
        # Ensure this translation actually works before saving it
        lang = kwargs.get('general', {}).get('primary_language')
        if lang:
            locale = Locale.parse(lang)
            t = Translator(locale, config['locale_dirs'])
            try:
                t._load_domain('mediacore')
            except LanguageError:
                # TODO: Show an error message on the language field
                kwargs['primary_language'] = None
        return self._save(general_form, 'general', values=kwargs)

    @expose('admin/settings/sitemaps.html')
    def sitemaps(self, **kwargs):
        return self._display(sitemaps_form, values=kwargs)

    @expose(request_method='POST')
    @validate(sitemaps_form, error_handler=general)
    @autocommit
    def sitemaps_save(self, **kwargs):
        """Save :class:`~mediacore.forms.admin.settings.SiteMapsForm`."""
        return self._save(sitemaps_form, 'sitemaps', values=kwargs)

    @expose('admin/settings/appearance.html')
    def appearance(self, **kwargs):
        return self._display(appearance_form, values=kwargs)

    @expose(request_method='POST')
    @validate(appearance_form, error_handler=appearance)
    @autocommit
    def appearance_save(self, **kwargs):
        """Save :class:`~mediacore.forms.admin.settings.appearanceForm`."""
        settings = request.settings
        accepted_extensions = ('.png', '.jpg', '.jpeg', '.gif')
        upload_field_filenames = [
            ('appearance_logo', 'logo'),
            ('appearance_background_image', 'bg_image'),
        ]

        #Handle a reset to defaults request first
        if kwargs.get('reset', None):
            self._update_settings(dict(appearance_settings))
            generate_appearance_css(appearance_settings)
            return redirect(controller='admin/settings', action='appearance')

        appearance_dir = os.path.join(config['cache.dir'], 'appearance')

        for field_name, file_name in upload_field_filenames:
            field = kwargs['general'].pop(field_name)
            if isinstance(field, FieldStorage):
                extension = os.path.splitext(field.filename)[1].lower()
                if extension in accepted_extensions:
                    #TODO: Need to sanitize manually here?
                    full_name = '%s%s' % (file_name, extension)
                    permanent_file = open(os.path.join(appearance_dir,
                                                       full_name), 'w')
                    shutil.copyfileobj(field.file, permanent_file)
                    permanent_file.close()
                    field.file.close()
                    kwargs['general'][field_name] = full_name
                    continue
            # Preserve existing setting
            kwargs['general'][field_name] = settings.get(field_name, '')

        self._save(appearance_form, values=kwargs)
        generate_appearance_css(
            [(key, setting.value) for key, setting in c.settings.iteritems()],
        )
        redirect(action='appearance')

    @expose('admin/settings/advertising.html')
    def advertising(self, **kwargs):
        return self._display(advertising_form, values=kwargs)

    @expose(request_method='POST')
    @validate(advertising_form, error_handler=general)
    @autocommit
    def advertising_save(self, **kwargs):
        """Save :class:`~mediacore.forms.admin.settings.AdvertisingForm`."""
        return self._save(advertising_form, 'advertising', values=kwargs)

    @expose('admin/settings/importvideos.html')
    def importvideos(self, **kwargs):
        category_tree = Category.query.order_by(Category.name).populated_tree()
        return dict(
            form = importvideos_form,
            form_values = kwargs,
            category_tree = category_tree,
        )

    @expose()
    @validate(importvideos_form, error_handler=importvideos)
    @autocommit
    def importvideos_save(self, youtube, **kwargs):
        """Save :class:`~mediacore.forms.admin.settings.ImportVideosForm`."""
        auto_publish = youtube.get('auto_publish', None)
        def extract_id_from_youtube_link(player_url):
            match = YoutubeStorage.url_pattern.match(player_url)
            if match is None:
                log.debug('Cannot parse YouTube URL: %s' % player_url)
                return None
            video_properties = match.groupdict()
            return video_properties.get('id')

        def video_already_has_media_file(player_url):
            unique_id = extract_id_from_youtube_link(player_url)
            if unique_id is None:
                return False
            return 0 != MediaFile.query.filter(MediaFile.unique_id==unique_id).count()

        def get_videos_from_feed(feed):
            for entry in feed.entry:
                # Occasionally, there are issues with a video in a feed
                # not being available (region restrictions, etc)
                # If this happens, just move along.
                if not entry.media.player:
                    log.debug('Video Feed Error: No player URL? %s' % entry)
                    continue
                video_url = unicode(entry.media.player.url, "utf-8")
                if video_already_has_media_file(video_url):
                    continue
                categories = kwargs.get('youtube.categories', None)
                tags = kwargs.get('youtube.tags', None)
                media = fetch_row(Media, u'new')
                user = request.environ['repoze.who.identity']['user']
                media.author = Author(user.display_name, user.email_address)
                media.reviewed = True
                media.title = unicode(entry.media.title.text, "utf-8")
                if entry.media.description.text:
                    encoded_description = unicode(entry.media.description.text,
                                                "utf-8")
                    media.description = clean_xhtml(encoded_description)
                media.slug = get_available_slug(Media, media.title, media)

                if tags:
                    media.set_tags(unicode(tags))
                if categories:
                    if not isinstance(categories, list):
                        categories = [categories]
                    media.set_categories(categories)
                try:
                    media_file = add_new_media_file(media,
                        url=video_url)
                except StorageError, e:
                    log.debug('Video Feed Error: Error storing video: %s at %s' \
                        % e.message, video_url)
                    continue
                if not has_thumbs(media):
                    create_default_thumbs_for(media)
                media.title = media_file.display_name
                media.update_status()
                if auto_publish:
                    media.reviewed = 1
                    media.encoded = 1
                    media.publishable = 1
                    media.created_on = datetime.now()
                    media.modified_on = datetime.now()
                    media.publish_on = datetime.now()
                DBSession.add(media)
                DBSession.flush()
        
        def import_videos_from_channel(channel_name, auto_publish):
            # Since we can only get 50 videos at a time, loop through when a "next"
            # link is present in the returned feed from YouTube
            getvideos = True
            yt_service = gdata.youtube.service.YouTubeService()
            uri = 'http://gdata.youtube.com/feeds/api/users/%s/uploads?max-results=50' \
                % (channel_name)
            while getvideos:
                feed = yt_service.GetYouTubeVideoFeed(uri)
                get_videos_from_feed(feed)
                for link in feed.link:
                    if link.rel == 'next':
                        uri = link.href
                        break
                else:
                    getvideos = False
            
        channel_names = youtube.get('channel_names', "")
        channel_names = channel_names.replace(',', ' ').split()
        try:
            for channel_name in channel_names:
                import_videos_from_channel(channel_name, auto_publish)
        except RequestError, request_error:
            if request_error.message['status'] != 403:
                raise
            c.form_errors['_the_form'] = "You have exceeded the traffic quota allowed by YouTube. " + \
                                         "While some of the videos have been saved, not all of them were imported correctly. " + \
                                         "Please wait a few minutes and run the import again in to continue."
            return self.importvideos(youtube=youtube, **kwargs)
        
        # Redirect to the Media view page, when the import is complete
        redirect(url_for(controller='admin/media', action='index'))
