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

from cgi import FieldStorage
from formencode import Invalid
from PIL import Image
from pylons import app_globals, config, request, response, session, tmpl_context as c
from repoze.what.predicates import has_permission
from sqlalchemy import orm, sql

from mediacore.forms.admin.settings import (AppearanceForm, APIForm,
    AnalyticsForm, CommentsForm, GeneralForm, NotificationsForm,
    PopularityForm, SiteMapsForm, UploadForm)
from mediacore.lib.base import BaseSettingsController
from mediacore.lib.decorators import expose, expose_xhr, paginate, validate
from mediacore.lib.helpers import redirect, url_for
from mediacore.lib.templating import render
from mediacore.model import Media, MultiSetting, Setting, fetch_row
from mediacore.model.meta import DBSession

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

    @expose()
    @validate(notifications_form, error_handler=notifications)
    def notifications_save(self, **kwargs):
        """Save :class:`~mediacore.forms.admin.settings.NotificationsForm`."""
        return self._save(notifications_form, 'notifications', values=kwargs)

    @expose('admin/settings/comments.html')
    def comments(self, **kwargs):
        return self._display(comments_form, values=kwargs)

    @expose()
    @validate(comments_form, error_handler=comments)
    def comments_save(self, **kwargs):
        """Save :class:`~mediacore.forms.admin.settings.CommentsForm`."""
        return self._save(comments_form, 'comments', values=kwargs)

    @expose('admin/settings/api.html')
    def api(self, **kwargs):
        return self._display(api_form, values=kwargs)

    @expose()
    @validate(api_form, error_handler=comments)
    def save_api(self, **kwargs):
        """Save :class:`~mediacore.forms.admin.settings.APIForm`."""
        return self._save(api_form, 'api', values=kwargs)

    @expose('admin/settings/popularity.html')
    def popularity(self, **kwargs):
        return self._display(popularity_form, values=kwargs)

    @expose()
    @validate(popularity_form, error_handler=popularity)
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

    @expose()
    @validate(upload_form, error_handler=upload)
    def upload_save(self, **kwargs):
        """Save :class:`~mediacore.forms.admin.settings.UploadForm`."""
        return self._save(upload_form, 'upload', values=kwargs)

    @expose('admin/settings/analytics.html')
    def analytics(self, **kwargs):
        return self._display(analytics_form, values=kwargs)

    @expose()
    @validate(analytics_form, error_handler=analytics)
    def analytics_save(self, **kwargs):
        """Save :class:`~mediacore.forms.admin.settings.AnalyticsForm`."""
        return self._save(analytics_form, 'analytics', values=kwargs)

    @expose('admin/settings/general.html')
    def general(self, **kwargs):
        return self._display(general_form, values=kwargs)

    @expose()
    @validate(general_form, error_handler=general)
    def general_save(self, **kwargs):
        """Save :class:`~mediacore.forms.admin.settings.GeneralForm`."""
        return self._save(general_form, 'general', values=kwargs)

    @expose('admin/settings/sitemaps.html')
    def sitemaps(self, **kwargs):
        return self._display(sitemaps_form, values=kwargs)

    @expose()
    @validate(sitemaps_form, error_handler=general)
    def sitemaps_save(self, **kwargs):
        """Save :class:`~mediacore.forms.admin.settings.SiteMapsForm`."""
        return self._save(sitemaps_form, 'sitemaps', values=kwargs)

    @expose('admin/settings/appearance.html')
    def appearance(self, **kwargs):
        return self._display(appearance_form, values=kwargs)

    @expose()
    @validate(appearance_form, error_handler=appearance)
    def appearance_save(self, **kwargs):
        """Save :class:`~mediacore.forms.admin.settings.appearanceForm`."""
        settings = app_globals.settings

        accepted_extensions = ('.png', '.jpg', '.jpeg', '.gif')
        appearance_dir = os.path.join(config['cache.dir'], 'appearance')
        upload_field_filenames = [
            ('appearance_logo', 'logo'),
            ('appearance_background_image', 'bg_image'),
        ]
        uikit_colors = {
            'white': {
                'btn_text_color': '#5c5c5e',
                'btn_text_shadow_color': '#fff',
                'btn_text_hover_color': '#4b4b4d'
            },
            'tan': {
                'btn_text_color': '#4a3430',
                'btn_text_shadow_color': '#fff',
                'btn_text_hover_color': '#4a3430'
            },
            'purple': {
                'btn_text_color': '#b0bcc5',
                'btn_text_shadow_color': '#000',
                'btn_text_hover_color': '#fff'
            },
            'blue': {
                'btn_text_color': '#fff',
                'btn_text_shadow_color': '#2d6dd1',
                'btn_text_hover_color': '#ddd'
            },
            'black': {
                'btn_text_color': '#797c7f',
                'btn_text_shadow_color': '#000',
                'btn_text_hover_color': '#ddd'
            },
            'green': {
                'btn_text_color': '#fff',
                'btn_text_shadow_color': '#000',
                'btn_text_hover_color': '#ddd'
            },
            'brown': {
                'btn_text_color': '#fff',
                'btn_text_shadow_color': '#000',
                'btn_text_hover_color': '#ddd'
            },
        }

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

        # Set vars to pass to our CSS template
        tmpl_vars = kwargs.copy()
        tmpl_vars['logo_height'] = Image.open(os.path.join(appearance_dir, \
            kwargs['general'].get('appearance_logo', 'logo.png'))).size[1]
        navbar_color = kwargs['general'].get(
            'appearance_navigation_bar_color', 'purple')
        tmpl_vars['navbar_color'] = navbar_color
        tmpl_vars['uikit_colors'] = uikit_colors.get(navbar_color)
        css_file = open(os.path.join(appearance_dir, 'appearance.css'), 'w')
        css_file.write(render('admin/settings/appearance_tmpl.css',
                              tmpl_vars, method='text'))
        css_file.close()

        return self._save(appearance_form, 'appearance', values=kwargs)
