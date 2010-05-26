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

from pylons import request, response, session, tmpl_context as c
from repoze.what.predicates import has_permission
from sqlalchemy import orm, sql

from mediacore.forms.admin.settings import AnalyticsForm, CommentsForm, DisplayForm, NotificationsForm, PopularityForm, UploadForm
from mediacore.lib.base import BaseController
from mediacore.lib.decorators import expose, expose_xhr, paginate, validate
from mediacore.lib.helpers import fetch_setting, redirect, url_for
from mediacore.model import Media, Setting, fetch_row
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


class SettingsController(BaseController):
    """
    Dumb controller for display and saving basic settings forms

    This maps forms from :class:`mediacore.forms.admin.settings` to our
    model :class:`~mediacore.model.settings.Setting`. This controller
    doesn't care what settings are used, the form dictates everything.
    The form field names should exactly match the name in the model,
    regardless of it's nesting in the form.

    If and when setting values need to be altered for display purposes,
    or before it is saved to the database, it should be done with a
    field validator instead of adding complexity here.

    """

    allow_only = has_permission('admin')

    def __before__(self, *args, **kwargs):
        """Load all our settings before each request."""
        BaseController.__before__(self, *args, **kwargs)
        c.settings = dict(DBSession.query(Setting.key, Setting))

    @expose()
    def index(self, **kwargs):
        redirect(controller='/admin/categories')

    def _update_settings(self, values):
        """Modify the settings associated with the given dictionary."""
        for name, value in values.iteritems():
            setting = c.settings[name]
            if value is None:
                value = u''
            else:
                value = unicode(value)
            if setting.value != value:
                setting.value = value
                DBSession.add(setting)
        DBSession.flush()

    def _display(self, form, **kwargs):
        """Return the template variables for display of the form.

        :rtype: dict
        :returns:
            form
                The passed in form instance.
            form_values
                ``dict`` form values
        """
        form_values = _nest_settings_for_form(c.settings, form)
        form_values.update(kwargs)
        return dict(
            form = form,
            form_values = form_values,
        )

    def _save(self, form, redirect_action=None, **kwargs):
        """Save the values from the passed in form instance."""
        values = _flatten_settings_from_form(c.settings, form, kwargs)
        self._update_settings(values)
        if redirect_action:
            redirect(action=redirect_action)


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

def _nest_settings_for_form(settings, form):
    """Create a dict of setting values nested to match the form."""
    form_values = {}
    for field in form.c:
        if isinstance(field, tw.forms.fields.ContainerMixin):
            form_values[field._name] = _nest_settings_for_form(settings, field)
        elif field._name in settings:
            form_values[field._name] = settings[field._name].value
    return form_values

def _flatten_settings_from_form(settings, form, form_values):
    """Take a nested dict and return a flat dict of setting values."""
    setting_values = {}
    for field in form.c:
        if isinstance(field, tw.forms.fields.ContainerMixin):
            setting_values.update(_flatten_settings_from_form(
                settings, field, form_values[field._name]
            ))
        elif field._name in settings:
            setting_values[field._name] = form_values[field._name]
    return setting_values
