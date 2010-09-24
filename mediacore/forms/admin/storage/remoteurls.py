# This file is a part of MediaCore, Copyright 2010 Simple Station Inc.
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

from formencode.validators import Int
from pylons.i18n import N_ as _

from mediacore.forms import ListFieldSet, TextField
from mediacore.forms.admin.storage import StorageForm
from mediacore.lib.storage.ftp import FTP_SERVER

class RTMPRemoteURLStorageForm(StorageForm):

    fields = StorageForm.fields + [
        ListFieldSet('rtmp',
            suppress_label=True,
            legend=_('RTMP Server Details:'),
            children=[
                TextField('server_uri', label_text=_('RTMP Server URL')),
            ]
        ),
    ] + StorageForm.buttons

    def display(self, value, **kwargs):
        engine = kwargs['engine']
        specifics = value.setdefault('rtmp', {})
        specifics.setdefault('server_uri', engine._data.get('rtmp_server_uri', None))
        return StorageForm.display(self, value, **kwargs)

    def save_engine_params(self, engine, specifics=None, **kwargs):
        """Map validated field values to engine data.

        Since form widgets may be nested or named differently than the keys
        in the :attr:`mediacore.lib.storage.StorageEngine._data` dict, it is
        necessary to manually map field values to the data dictionary.

        :type engine: :class:`mediacore.lib.storage.StorageEngine` subclass
        :param engine: An instance of the storage engine implementation.
        :param \*\*kwargs: Validated and filtered form values.
        :raises formencode.Invalid: If some post-validation error is detected
            in the user input. This will trigger the same error handling
            behaviour as with the @validate decorator.

        """
        engine._data['rtmp_server_uri'] = specifics['rtmp_server_uri'] or None
