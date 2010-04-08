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

from tg import config, request, response, tmpl_context
from sqlalchemy import orm, sql
from repoze.what.predicates import has_permission
import tw.forms.fields

from mediacore.lib.base import (BaseController, url_for, redirect,
    expose, expose_xhr, validate, paginate)
from mediacore.model import DBSession, fetch_row, Setting
from mediacore.model.settings import fetch_setting
from mediacore.forms.admin.settings import NotificationsForm, DisplaySettingsForm

notifications_form = NotificationsForm(
    action=url_for(controller='/admin/settings', action='save_notifications'))
display_form = DisplaySettingsForm(
    action=url_for(controller='/admin/settings', action='save_display'))


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

    def __init__(self, *args, **kwargs):
        super(SettingsController, self).__init__(*args, **kwargs)
        self.settings = dict(DBSession.query(Setting.key, Setting))

    def _update_settings(self, values):
        """Modify the settings associated with the given dictionary."""
        for name, value in values.iteritems():
            if self.settings[name].value != value:
                self.settings[name].value = value
                DBSession.add(self.settings[name])
        DBSession.flush()

    @expose('mediacore.templates.admin.settings.notifications')
    def notifications(self, **kwargs):
        """Display the form.

        :rtype: dict
        :returns:
            settings_form
                The :class:`~mediacore.forms.admin.settings.NotificationsForm`
                instance.
            settings_values
                ``dict`` form values

        """
        form = notifications_form
        form_values = _nest_settings_for_form(self.settings, form)
        form_values.update(kwargs)
        return dict(
            form = form,
            form_values = form_values,
        )

    @expose()
    @validate(notifications_form, error_handler=notifications)
    def save_notifications(self, **kwargs):
        """Save :class:`~mediacore.forms.admin.settings.NotificationsForm`."""
        form = notifications_form
        values = _flatten_settings_from_form(self.settings, form, kwargs)
        self._update_settings(values)
        redirect(action='notifications')

    @expose('mediacore.templates.admin.settings.display')
    def display(self, **kwargs):
        """Display the form.

        :rtype: dict
        :returns:
            settings_form
                The :class:`~mediacore.forms.admin.settings.NotificationsForm`
                instance.
            settings_values
                ``dict`` form values

        """
        form = display_form
        form_values = _nest_settings_for_form(self.settings, form)
        form_values.update(kwargs)
        return dict(
            form = form,
            form_values = form_values,
        )

    @expose()
    @validate(display_form, error_handler=display)
    def save_display(self, **kwargs):
        """Save :class:`~mediacore.forms.admin.settings.DisplaySettingsForm`."""
        form = display_form
        values = _flatten_settings_from_form(self.settings, form, kwargs)
        self._update_settings(values)
        redirect(action='display')


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
