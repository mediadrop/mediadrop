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

from pylons import request
from pylons.i18n import N_ as _
from tw.forms import PasswordField, RadioButtonList, SingleSelectField
from tw.forms.fields import ContainerMixin as _ContainerMixin
from tw.forms.validators import All, FancyValidator, FieldsMatch, Invalid, NotEmpty, PlainText, Schema, StringBool

from mediacore.forms import ListFieldSet, ListForm, SubmitButton, TextField
from mediacore.plugin import events
from mediacore.plugin.abc import abstractmethod

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
            legend=_('General Options:'),
            suppress_label=True,
            children=[
                TextField('display_name',
                    label_text=_('Display Name'),
                    validator=TextField.validator(not_empty=True),
                    maxlength=100,
                ),
            ],
        ),
    ]

    buttons = [
        SubmitButton('save',
            default=_('Save'),
            named_button=True,
            css_classes=['btn', 'btn-save', 'blue', 'f-rgt'],
        ),
        SubmitButton('delete',
            default=_('Delete'),
            named_button=True,
            css_classes=['btn', 'btn-delete', 'f-lft'],
        ),
    ]

#    def display(self, value, **kwargs):
#        """Display the form with default values from the engine param."""
#        return ListForm.display(self, value, **kwargs)

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
            options=(
                (False, _('Yes, use the Flash Player when the device supports it.')),
                (True, _('No, use the HTML5 Player when the device supports it.')),
            ),
            label_text=_('Prefer the Flash Player when possible'),
            validator=StringBool,
        ),
    ] + PlayerPrefsForm.buttons

    def display(self, value, **kwargs):
        """Display the form with default values from the engine param."""
        player = kwargs['player']
        value.setdefault('prefer_flash', player.data.get('prefer_flash', False))
        return PlayerPrefsForm.display(self, value, **kwargs)

    def save_data(self, player, prefer_flash, **kwargs):
        player.data['prefer_flash'] = prefer_flash

class SublimePlayerPrefsForm(PlayerPrefsForm):
    fields = [
        TextField('script_tag',
            label_text=_('Script Tag'),
            help_text=_('The unique script tag given for your site.'),
        ),
    ] + PlayerPrefsForm.buttons

    def display(self, value, **kwargs):
        """Display the form with default values from the engine param."""
        player = kwargs['player']
        value.setdefault('script_tag', player.data.get('script_tag', ''))
        return PlayerPrefsForm.display(self, value, **kwargs)

    def save_data(self, player, script_tag, **kwargs):
        player.data['script_tag'] = script_tag or None
        if not script_tag and player.enabled:
            player.enabled = False
