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

from mediacore.forms.admin.settings import AnalyticsForm, CommentsForm, DisplayForm, NotificationsForm, PopularityForm, RTMPForm, UploadForm
from mediacore.lib.base import BaseSettingsController
from mediacore.lib.decorators import expose, expose_xhr, paginate, validate
from mediacore.lib.helpers import redirect, url_for
from mediacore.model import Media, MultiSetting, Setting, fetch_row
from mediacore.model.meta import DBSession

import logging
log = logging.getLogger(__name__)

notifications_form = NotificationsForm(
    action=url_for(controller='/admin/settings', action='save_notifications'))

comments_form = CommentsForm(
    action=url_for(controller='/admin/settings', action='save_comments'))

display_form = DisplayForm(
    action=url_for(controller='/admin/settings', action='save_display'))

popularity_form = PopularityForm(
    action=url_for(controller='/admin/settings', action='save_popularity'))

upload_form = UploadForm(
    action=url_for(controller='/admin/settings', action='save_upload'))

analytics_form = AnalyticsForm(
    action=url_for(controller='/admin/settings', action='save_analytics'))

rtmp_form = RTMPForm(
    action=url_for(controller='/admin/settings', action='save_rtmp'))

class SettingsController(BaseSettingsController):
    """
    Dumb controller for display and saving basic settings forms.

    See :class:`mediacore.lib.base.BaseSettingsController` for more details.

    """
    @expose()
    def index(self, **kwargs):
        redirect(controller='/admin/categories')

    @expose('admin/settings/notifications.html')
    def notifications(self, **kwargs):
        return self._display(notifications_form, **kwargs)

    @expose()
    @validate(notifications_form, error_handler=notifications)
    def save_notifications(self, **kwargs):
        """Save :class:`~mediacore.forms.admin.settings.NotificationsForm`."""
        return self._save(notifications_form, 'notifications', **kwargs)

    @expose('admin/settings/comments.html')
    def comments(self, **kwargs):
        return self._display(comments_form, **kwargs)

    @expose()
    @validate(comments_form, error_handler=comments)
    def save_comments(self, **kwargs):
        """Save :class:`~mediacore.forms.admin.settings.CommentsForm`."""
        return self._save(comments_form, 'comments', **kwargs)

    @expose('admin/settings/display.html')
    def display(self, **kwargs):
        return self._display(display_form, **kwargs)

    @expose()
    @validate(display_form, error_handler=display)
    def save_display(self, **kwargs):
        """Save :class:`~mediacore.forms.admin.settings.DisplayForm`."""
        player_type = c.settings['player_type'].value
        self._save(display_form, **kwargs)
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
        return self._display(popularity_form, **kwargs)

    @expose()
    @validate(popularity_form, error_handler=popularity)
    def save_popularity(self, **kwargs):
        """Save :class:`~mediacore.forms.admin.settings.PopularityForm`.

        Updates the popularity for every media item based on the submitted
        values.
        """
        self._save(popularity_form, **kwargs)
        for m in Media.query:
            m.update_popularity()
            DBSession.add(m)
        redirect(action='popularity')

    @expose('admin/settings/upload.html')
    def upload(self, **kwargs):
        return self._display(upload_form, **kwargs)

    @expose()
    @validate(upload_form, error_handler=upload)
    def save_upload(self, **kwargs):
        """Save :class:`~mediacore.forms.admin.settings.UploadForm`."""
        return self._save(upload_form, 'upload', **kwargs)

    @expose('admin/settings/analytics.html')
    def analytics(self, **kwargs):
        return self._display(analytics_form, **kwargs)

    @expose()
    @validate(analytics_form, error_handler=analytics)
    def save_analytics(self, **kwargs):
        """Save :class:`~mediacore.forms.admin.settings.AnalyticsForm`."""
        return self._save(analytics_form, 'analytics', **kwargs)

    @expose('admin/settings/rtmp.html')
    def rtmp(self, **kwargs):
        return dict(
            form = rtmp_form,
            form_values = {},
        )

    @expose()
    @validate(rtmp_form, error_handler=rtmp)
    def save_rtmp(self, new_rtmp_url=None, old_rtmp_id=None, delete=None, **kwargs):
        """Save :class:`~mediacore.forms.admin.settings.RTMPForm`."""
        if delete:
            s = fetch_row(MultiSetting, old_rtmp_id, key=u'rtmp_server')
            DBSession.delete(s)
        elif new_rtmp_url:
            s = MultiSetting(u'rtmp_server', new_rtmp_url)
            DBSession.add(s)
        redirect(controller='/admin/settings', action='rtmp')
