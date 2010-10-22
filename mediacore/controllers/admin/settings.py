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

import tw.forms.fields

from pylons import app_globals, request, response, session, tmpl_context as c
from repoze.what.predicates import has_permission
from sqlalchemy import orm, sql

from mediacore.forms.admin.settings import APIForm, AnalyticsForm, CommentsForm, DisplayForm, NotificationsForm, PopularityForm, UploadForm
from mediacore.lib.base import BaseSettingsController
from mediacore.lib.decorators import expose, expose_xhr, paginate, validate
from mediacore.lib.helpers import redirect, url_for
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

display_form = DisplayForm(
    action=url_for(controller='/admin/settings', action='display_save'))

popularity_form = PopularityForm(
    action=url_for(controller='/admin/settings', action='popularity_save'))

upload_form = UploadForm(
    action=url_for(controller='/admin/settings', action='upload_save'))

analytics_form = AnalyticsForm(
    action=url_for(controller='/admin/settings', action='analytics_save'))

class SettingsController(BaseSettingsController):
    """
    Dumb controller for display and saving basic settings forms.

    See :class:`mediacore.lib.base.BaseSettingsController` for more details.

    """
    @expose()
    def index(self, **kwargs):
        redirect(action='analytics')

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

    @expose('admin/settings/display.html')
    def display(self, **kwargs):
        return self._display(display_form, values=kwargs)

    @expose()
    @validate(display_form, error_handler=display)
    def display_save(self, **kwargs):
        """Save :class:`~mediacore.forms.admin.settings.DisplayForm`."""
        player_type = c.settings['player_type'].value
        self._save(display_form, values=kwargs)
        # If the player_type changes, we must update the Media.encoded flag,
        # since some things may play now and/or not play anymore with the
        # new setting.
        if player_type != c.settings['player_type'].value:
            for m in Media.query.options(orm.eagerload('files')):
                m.update_status()
                DBSession.add(m)
        redirect(action='display')

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
