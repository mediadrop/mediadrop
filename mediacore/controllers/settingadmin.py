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
from mediacore.lib import helpers
from mediacore.model import DBSession, fetch_row, Setting
from mediacore.forms.settings import SettingsForm, DisplaySettingsForm

settings_form = SettingsForm(
    action=url_for(controller='/settingadmin', action='save'))
display_settings_form = DisplaySettingsForm(
    action=url_for(controller='/settingadmin', action='save_display'))


class SettingadminController(BaseController):
    allow_only = has_permission('admin')

    @expose()
    def index(self, section='topics', **kwargs):
        redirect(controller='categoryadmin', category=section)


    @expose('mediacore.templates.admin.settings.edit')
    def edit(self, **kwargs):
        """Display the :class:`~mediacore.forms.settings.SettingsForm`.

        :rtype: dict
        :returns:
            settings_form
                The :class:`~mediacore.forms.settings.SettingsForm` instance.
            settings_values
                ``dict`` form values

        """
        if tmpl_context.action == 'save' and len(kwargs) > 0:
            # Use the values from error_handler or GET for new users
            settings_values = dict(
                email = dict(
                    media_uploaded = kwargs['email.media_uploaded'],
                    comment_posted = kwargs['email.comment_posted'],
                    support_requests = kwargs['email.support_requests'],
                    send_from = kwargs['email.send_from'],
                ),
#                ftp = dict(
#                    server = kwargs['ftp.server'],
#                    username = kwargs['ftp.username'],
#                    upload_path = kwargs['ftp.upload_path'],
#                    download_url = kwargs['ftp.download_url'],
#                ),
                legal_wording = dict(
                    user_uploads = kwargs['legal_wording.user_uploads'],
                ),
            )
            settings_values = kwargs
            settings_values['ftp.password'] =  settings_values['ftp.confirm_password'] = None
        else:
            settings = self._fetch_keyed_settings()
            settings_values = dict(
                email = dict(
                    media_uploaded = settings['email_media_uploaded'].value,
                    comment_posted = settings['email_comment_posted'].value,
                    support_requests = settings['email_support_requests'].value,
                    send_from = settings['email_send_from'].value,
                ),
#                ftp = dict(
#                    server = settings['ftp_server'].value,
#                    username = settings['ftp_username'].value,
#                    upload_path = settings['ftp_upload_path'].value,
#                    download_url = settings['ftp_download_url'].value,
#                ),
                legal_wording = dict(
                    user_uploads = settings['wording_user_uploads'].value,
                ),
                default_wording = dict(
                    additional_notes = settings['wording_additional_notes'].value,
                ),
            )

        return dict(
            settings_form = settings_form,
            settings_values = settings_values,
        )

    @expose()
    @validate(settings_form, error_handler=edit)
    def save(self, email, legal_wording, default_wording, **kwargs):
        """Save :class:`~mediacore.forms.settings.SettingsForm`.

        Redirects back to :meth:`edit` after successful editing.

        """
        settings = self._fetch_keyed_settings()
        settings['email_media_uploaded'].value = email['media_uploaded']
        settings['email_comment_posted'].value = email['comment_posted']
        settings['email_support_requests'].value = email['support_requests']
        settings['email_send_from'].value = email['send_from']
#        settings['ftp_server'].value = ftp['server']
#        settings['ftp_username'].value = ftp['username']
#        if ftp['password'] is not None and ftp['password'] != '':
#            settings['ftp_password'].value = ftp['password']
#        settings['ftp_upload_path'].value = ftp['upload_path']
#        settings['ftp_download_url'].value = ftp['download_url']
        settings['wording_user_uploads'].value = legal_wording['user_uploads']
        settings['wording_additional_notes'].value = default_wording['additional_notes']

        DBSession.add_all(settings.values())
        DBSession.flush()
        redirect(action='edit')

    @expose('mediacore.templates.admin.settings.edit_display')
    def edit_display(self, **kwargs):
        """Display the :class:`~mediacore.forms.settings.SettingsForm`.

        :rtype: dict
        :returns:
            settings_form
                The :class:`~mediacore.forms.settings.SettingsForm` instance.
            settings_values
                ``dict`` form values

        """
        if tmpl_context.action == 'save' and len(kwargs) > 0:
            # Use the values from error_handler or GET for new users
            settings_values = kwargs
        else:
            settings_values = dict(
                tinymce = bool(helpers.fetch_setting('enable_tinymce'))
            )

        return dict(
            display_settings_form = display_settings_form,
            settings_values = settings_values,
        )

    @expose()
    @validate(display_settings_form, error_handler=edit_display)
    def save_display(self, tinymce, **kwargs):
        rich_setting = fetch_row(Setting, key='enable_tinymce')

        if tinymce:
            rich_setting.value = 'enabled'
        else:
            rich_setting.value = None

        DBSession.add(rich_setting)
        DBSession.flush()
        redirect(action='edit_display')


    def _fetch_keyed_settings(self):
        """Return a dictionary of settings keyed by the setting.key."""
        settings = DBSession.query(Setting).all()
        return dict((setting.key, setting) for setting in settings)

