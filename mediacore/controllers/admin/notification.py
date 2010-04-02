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

settings_form = SettingsForm(
    action=url_for(controller='/admin/notification', action='save'))


class NotificationController(BaseController):
    allow_only = has_permission('admin')

    @expose('mediacore.templates.admin.settings.notifications.edit')
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
    @validate(settings_form, error_handler=index)
    def save(self, email, legal_wording, default_wording, **kwargs):
        """Save :class:`~mediacore.forms.admin.settings.settings.SettingsForm`.

        Redirects back to :meth:`index` after successful editing.

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
        redirect(action='index')


    def _fetch_keyed_settings(self):
        """Return a dictionary of settings keyed by the setting.key."""
        settings = DBSession.query(Setting).all()
        return dict((setting.key, setting) for setting in settings)

