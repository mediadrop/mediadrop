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

from mediacore.lib.base import (BaseController, url_for, redirect,
    expose, expose_xhr, validate, paginate)
from mediacore.lib.helpers import fetch_setting
from mediacore.model import DBSession, fetch_row, Setting
from mediacore.forms.admin.settings.settings import SettingsForm, DisplaySettingsForm

display_settings_form = DisplaySettingsForm(
    action=url_for(controller='/admin/display', action='save'))


class DisplayController(BaseController):
    allow_only = has_permission('admin')

    @expose('mediacore.templates.admin.settings.display.edit')
    def index(self, **kwargs):
        """Display the :class:`~mediacore.forms.admin.settings.settings.SettingsForm`.

        :rtype: dict
        :returns:
            settings_form
                The :class:`~mediacore.forms.admin.settings.settings.SettingsForm` instance.
            settings_values
                ``dict`` form values

        """
        if tmpl_context.action == 'save' and len(kwargs) > 0:
            # Use the values from error_handler or GET for new users
            settings_values = kwargs
        else:
            settings_values = dict(
                tinymce = bool(fetch_setting('enable_tinymce')),
                popularity = dict(
                    decay_exponent = fetch_setting('popularity_decay_exponent'),
                    decay_lifetime = fetch_setting('popularity_decay_lifetime')
                ),
                player = fetch_setting('player'),
            )

        return dict(
            display_settings_form = display_settings_form,
            settings_values = settings_values,
        )

    @expose()
    @validate(display_settings_form, error_handler=index)
    def save(self, tinymce, popularity, player, **kwargs):
        rich_setting = fetch_row(Setting, key='enable_tinymce')
        decay_exponent = fetch_row(Setting, key='popularity_decay_exponent')
        decay_lifetime = fetch_row(Setting, key='popularity_decay_lifetime')
        player_setting = fetch_row(Setting, key='player')

        if tinymce:
            rich_setting.value = 'enabled'
        else:
            rich_setting.value = None

        decay_exponent.value = popularity['decay_exponent']
        decay_lifetime.value = popularity['decay_lifetime']
        player_setting.value = player

        DBSession.add(rich_setting)
        DBSession.add(decay_exponent)
        DBSession.add(decay_lifetime)
        DBSession.add(player_setting)
        DBSession.flush()
        redirect(action='index')

