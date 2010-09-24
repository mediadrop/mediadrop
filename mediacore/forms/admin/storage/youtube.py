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

import logging

from pylons.i18n import N_ as _
from tw.forms.fields import CheckBox

from mediacore.forms import ListFieldSet, TextField
from mediacore.forms.admin.storage import StorageForm

log = logging.getLogger(__name__)

class YoutubeStorageForm(StorageForm):

    fields = StorageForm.fields + [
        ListFieldSet('player',
            suppress_label=True,
            legend=_('Player Options:'),
            children=[
                CheckBox('disablekb', label_text=_('Disable the player keyboard controls.')),
                CheckBox('fs', label_text=_('Enable fullscreen.')),
                CheckBox('hd', label_text=_('Enable high-def quality by default.')),
                CheckBox('rel', label_text=_('Allow the player to load related videos once playback of the initial video starts. Related videos are displayed in the "genie menu" when the menu button is pressed.')),
                CheckBox('showsearch', label_text=_('Show the search box when the video is minimized. The above option must be enabled for this to work.')),
                CheckBox('showinfo', label_text=_('Display information like the video title and rating before the video starts playing.')),
                CheckBox('nocookie', label_text=_('Enable privacy-enhanced mode.')),
            ],
        )
    ] + StorageForm.buttons

    player_params = ('disablekb', 'fs', 'hd', 'rel', 'showsearch', 'showinfo')

    def display(self, value, **kwargs):
        engine = kwargs['engine']
        player_data = engine._data.get('player_params', {})
        player = value.setdefault('player', {})
        player.setdefault('nocookie', engine._data.get('nocookie', False))
        for x in self.player_params:
            player.setdefault(x, player_data.get(x, False))
        return StorageForm.display(self, value, **kwargs)

    def save_engine_params(self, engine, player=None, **kwargs):
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
        engine._data['nocookie'] = player['nocookie']
        player_params = engine._data['player_params']
        for x in self.player_params:
            player_params[x] = player[x]
