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
import logging
from formencode.validators import Int

from pylons import request
from tw.forms import CheckBox, PasswordField, RadioButtonList, SingleSelectField
from tw.forms.fields import ContainerMixin as _ContainerMixin
from tw.forms.validators import All, FancyValidator, FieldsMatch, Invalid, NotEmpty, PlainText, Schema, StringBool

from mediacore.forms import ListFieldSet, ListForm, SubmitButton, ResetButton, TextField
from mediacore.lib.i18n import N_, _
from mediacore.lib.util import merge_dicts
from mediacore.plugin import events
from mediacore.plugin.abc import abstractmethod

log = logging.getLogger(__name__)

class PlayerPrefsForm(ListForm):
    template = 'admin/box-form.html'
    id = 'player-form'
    css_class = 'form playerform'
    submit_text = None
    show_children_errors = True
    _name = 'player-form' # TODO: Figure out why this is required??
    params = ['player']

    fields = [
        ListFieldSet('general',
            legend=N_('General Options:'),
            suppress_label=True,
            children=[
                TextField('display_name',
                    label_text=N_('Display Name'),
                    validator=TextField.validator(not_empty=True),
                    maxlength=100,
                ),
            ],
        ),
    ]

    buttons = [
        SubmitButton('save',
            default=N_('Save'),
            css_classes=['btn', 'btn-save', 'blue', 'f-rgt'],
        ),
    ]

    def display(self, value, player, **kwargs):
        """Display the form with default values from the given player.

        If the value dict is not fully populated, populate any missing entries
        with the values from the given player's
        :attr:`_data <mediacore.model.player.PlayerPrefs._data>` dict.

        :param value: A (sparse) dict of values to populate the form with.
        :type value: dict
        :param player: The player prefs mapped object to retrieve the default
            values from.
        :type player: :class:`mediacore.model.player.PlayerPrefs` subclass

        """
        return ListForm.display(self, value, **kwargs)

    def save_data(self, player, **kwargs):
        """Map validated field values to `PlayerPrefs.data`.

        Since form widgets may be nested or named differently than the keys
        in the :attr:`mediacore.lib.storage.StorageEngine._data` dict, it is
        necessary to manually map field values to the data dictionary.

        :type player: :class:`mediacore.model.player.PlayerPrefs` subclass
        :param player: The player prefs mapped object to store the data in.
        :param \*\*kwargs: Validated and filtered form values.
        :raises formencode.Invalid: If some post-validation error is detected
            in the user input. This will trigger the same error handling
            behaviour as with the @validate decorator.

        """

class HTML5OrFlashPrefsForm(PlayerPrefsForm):
    fields = [
        RadioButtonList('prefer_flash',
            options=lambda: (
                (False, _('Yes, use the Flash Player when the device supports it.')),
                (True, _('No, use the HTML5 Player when the device supports it.')),
            ),
            css_classes=['options'],
            label_text=N_('Prefer the Flash Player when possible'),
            validator=StringBool,
        ),
    ] + PlayerPrefsForm.buttons

    def display(self, value, player, **kwargs):
        value.setdefault('prefer_flash', player.data.get('prefer_flash', False))
        return PlayerPrefsForm.display(self, value, player, **kwargs)

    def save_data(self, player, prefer_flash, **kwargs):
        player.data['prefer_flash'] = prefer_flash

class SublimePlayerPrefsForm(PlayerPrefsForm):
    fields = [
        TextField('script_tag',
            label_text=N_('Script Tag'),
            help_text=N_('The unique script tag given for your site.'),
        ),
    ] + PlayerPrefsForm.buttons

    def display(self, value, player, **kwargs):
        value.setdefault('script_tag', player.data.get('script_tag', ''))
        return PlayerPrefsForm.display(self, value, player, **kwargs)

    def save_data(self, player, script_tag, **kwargs):
        player.data['script_tag'] = script_tag or None
        if not script_tag and player.enabled:
            player.enabled = False

class YoutubeFlashPlayerPrefsForm(PlayerPrefsForm):
    fields = [
        ListFieldSet('options',
            suppress_label=True,
            legend=N_('Player Options:'),
            children=[
                RadioButtonList('version',
                    options=lambda: (
                        (2, _('Use the deprecated AS2 player.')),
                        (3, _('Use the AS3 player.')),
                    ),
                    label_text=N_("YouTube player version"),
                    validator=Int,
                ),
                RadioButtonList('iv_load_policy',
                    options=lambda: (
                        (1, _('Show video annotations by default.')),
                        (3, _('Hide video annotations by default.')),
                    ),
                    label_text=N_("Video annotations"),
                    validator=Int,
                ),
                CheckBox('disablekb', label_text=N_('Disable the player keyboard controls.')),
                CheckBox('autoplay', label_text=N_('Autoplay the video video when the player loads.')),
                CheckBox('modestbranding', label_text=N_('Do not show a YouTube logo in the player controls'), help_text=N_("Supported by AS3 only.")),
                CheckBox('fs', label_text=N_('Enable fullscreen.')),
                CheckBox('hd', label_text=N_('Enable high-def quality by default.'), help_text=N_("The AS3 player will automatically play the version of the video that is appropriate for your player's size.")),
                CheckBox('rel', label_text=N_('Load related videos once playback of the initial video starts. Related videos are displayed in the "genie menu" when the menu button is pressed.')),
                CheckBox('showsearch', label_text=N_('Show the search box when the video is minimized. The related videos option must be enabled for this to work.')),
                CheckBox('showinfo', label_text=N_('Display information like the video title and rating before the video starts playing.')),
                RadioButtonList('autohide',
                    options=lambda: (
                        (0, _('Always show player controls.')),
                        (1, _('Autohide all player controls after a video starts playing.')),
                        (2, _('Autohide only the progress bar after a video starts playing.')),
                    ),
                    label_text=N_("Player control hiding"),
                    validator=Int,
                ),
            ],
            css_classes=['options'],
        )
    ] + PlayerPrefsForm.buttons

    def display(self, value, player, **kwargs):
        newvalue = {}
        defaults = {'options': player.data}
        merge_dicts(newvalue, defaults, value)
        return PlayerPrefsForm.display(self, newvalue, player, **kwargs)

    def save_data(self, player, options, **kwargs):
        for field, value in options.iteritems():
            player.data[field] = int(value)
