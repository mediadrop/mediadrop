# This file is a part of MediaDrop (http://www.mediadrop.net),
# Copyright 2009-2013 MediaDrop contributors
# For the exact contribution history, see the git revision log.
# The source code contained in this file is licensed under the GPLv3 or
# (at your option) any later version.
# See LICENSE.txt in the main project directory, for more information.

import os
import shutil

from cgi import FieldStorage
from babel.core import Locale
from pylons import config, request, tmpl_context as c

from mediadrop.forms.admin.settings import (AdvertisingForm, AppearanceForm,
    APIForm, AnalyticsForm, CommentsForm, GeneralForm,
    NotificationsForm, PopularityForm, SiteMapsForm, UploadForm)
from mediadrop.lib.base import BaseSettingsController
from mediadrop.lib.decorators import autocommit, expose, observable, validate
from mediadrop.lib.helpers import filter_vulgarity, redirect, url_for
from mediadrop.lib.i18n import LanguageError, Translator
from mediadrop.model import Comment, Media
from mediadrop.model.meta import DBSession
from mediadrop.plugin import events
from mediadrop.websetup import appearance_settings, generate_appearance_css

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


class SettingsController(BaseSettingsController):
    """
    Dumb controller for display and saving basic settings forms.

    See :class:`mediadrop.lib.base.BaseSettingsController` for more details.

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
    @observable(events.Admin.SettingsController.notifications_save)
    def notifications_save(self, **kwargs):
        """Save :class:`~mediadrop.forms.admin.settings.NotificationsForm`."""
        return self._save(notifications_form, 'notifications', values=kwargs)

    @expose('admin/settings/comments.html')
    def comments(self, **kwargs):
        return self._display(comments_form, values=kwargs)

    @expose(request_method='POST')
    @validate(comments_form, error_handler=comments)
    @autocommit
    @observable(events.Admin.SettingsController.comments_save)
    def comments_save(self, **kwargs):
        """Save :class:`~mediadrop.forms.admin.settings.CommentsForm`."""
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
    @observable(events.Admin.SettingsController.save_api)
    def save_api(self, **kwargs):
        """Save :class:`~mediadrop.forms.admin.settings.APIForm`."""
        return self._save(api_form, 'api', values=kwargs)

    @expose('admin/settings/popularity.html')
    def popularity(self, **kwargs):
        return self._display(popularity_form, values=kwargs)

    @expose(request_method='POST')
    @validate(popularity_form, error_handler=popularity)
    @autocommit
    @observable(events.Admin.SettingsController.popularity_save)
    def popularity_save(self, **kwargs):
        """Save :class:`~mediadrop.forms.admin.settings.PopularityForm`.

        Updates the popularity for every media item based on the submitted
        values.
        """
        self._save(popularity_form, values=kwargs)
        # ".util.calculate_popularity()" uses the popularity settings from
        # the request.settings which are only updated when a new request
        # comes in.
        # update the settings manually so the popularity is actually updated
        # correctly.
        for key in ('popularity_decay_exponent', 'popularity_decay_lifetime'):
            request.settings[key] = kwargs['popularity.'+key]
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
    @observable(events.Admin.SettingsController.upload_save)
    def upload_save(self, **kwargs):
        """Save :class:`~mediadrop.forms.admin.settings.UploadForm`."""
        return self._save(upload_form, 'upload', values=kwargs)

    @expose('admin/settings/analytics.html')
    def analytics(self, **kwargs):
        return self._display(analytics_form, values=kwargs)

    @expose(request_method='POST')
    @validate(analytics_form, error_handler=analytics)
    @autocommit
    @observable(events.Admin.SettingsController.analytics_save)
    def analytics_save(self, **kwargs):
        """Save :class:`~mediadrop.forms.admin.settings.AnalyticsForm`."""
        return self._save(analytics_form, 'analytics', values=kwargs)

    @expose('admin/settings/general.html')
    def general(self, **kwargs):
        if not c.settings['primary_language'].value:
            kwargs.setdefault('general', {}).setdefault('primary_language', 'en')
        return self._display(general_form, values=kwargs)

    @expose(request_method='POST')
    @validate(general_form, error_handler=general)
    @autocommit
    @observable(events.Admin.SettingsController.general_save)
    def general_save(self, **kwargs):
        """Save :class:`~mediadrop.forms.admin.settings.GeneralForm`."""
        # Ensure this translation actually works before saving it
        lang = kwargs.get('general', {}).get('primary_language')
        if lang:
            locale = Locale.parse(lang)
            t = Translator(locale, config['locale_dirs'])
            try:
                t._load_domain('mediadrop')
            except LanguageError:
                # TODO: Show an error message on the language field
                kwargs['primary_language'] = None
        return self._save(general_form, 'general', values=kwargs)

    @expose('admin/settings/sitemaps.html')
    def sitemaps(self, **kwargs):
        return self._display(sitemaps_form, values=kwargs)

    @expose(request_method='POST')
    @validate(sitemaps_form, error_handler=sitemaps)
    @autocommit
    @observable(events.Admin.SettingsController.sitemaps_save)
    def sitemaps_save(self, **kwargs):
        """Save :class:`~mediadrop.forms.admin.settings.SiteMapsForm`."""
        return self._save(sitemaps_form, 'sitemaps', values=kwargs)

    @expose('admin/settings/appearance.html')
    def appearance(self, **kwargs):
        return self._display(appearance_form, values=kwargs)

    @expose(request_method='POST')
    @validate(appearance_form, error_handler=appearance)
    @autocommit
    @observable(events.Admin.SettingsController.appearance_save)
    def appearance_save(self, **kwargs):
        """Save :class:`~mediadrop.forms.admin.settings.appearanceForm`."""
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

        appearance_dir = os.path.join(config['pylons.cache_dir'], 'appearance')

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
    @observable(events.Admin.SettingsController.advertising_save)
    def advertising_save(self, **kwargs):
        """Save :class:`~mediadrop.forms.admin.settings.AdvertisingForm`."""
        return self._save(advertising_form, 'advertising', values=kwargs)

