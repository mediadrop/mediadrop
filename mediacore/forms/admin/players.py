# This file is a part of MediaDrop (http://www.mediadrop.net),
# Copyright 2009-2013 MediaDrop contributors
# For the exact contribution history, see the git revision log.
# The source code contained in this file is licensed under the GPLv3 or
# (at your option) any later version.
# See LICENSE.txt in the main project directory, for more information.
import logging
from formencode.validators import Int

from tw.forms import CheckBox, RadioButtonList
from tw.forms.validators import StringBool

from mediacore.forms import ListFieldSet, ListForm, SubmitButton, TextField
from mediacore.lib.i18n import N_, _
from mediacore.lib.util import merge_dicts
from mediacore.plugin import events

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
    
    event = events.Admin.Players.HTML5OrFlashPrefsForm

    def display(self, value, player, **kwargs):
        value.setdefault('prefer_flash', player.data.get('prefer_flash', False))
        return PlayerPrefsForm.display(self, value, player, **kwargs)

    def save_data(self, player, prefer_flash, **kwargs):
        player.data['prefer_flash'] = prefer_flash

class SublimePlayerPrefsForm(PlayerPrefsForm):
    event = events.Admin.Players.SublimePlayerPrefsForm
    
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

class YoutubePlayerPrefsForm(PlayerPrefsForm):
    event = events.Admin.Players.YoutubeFlashPlayerPrefsForm
    
    fields = [
        ListFieldSet('options',
            suppress_label=True,
            legend=N_('Player Options:'),
            children=[
                RadioButtonList('version',
                    options=lambda: (
                        (2, _('Use the deprecated AS2 player.')),
                        (3, _('Use the AS3/HTML5 player.')),
                    ),
                    css_label_classes=['container-list-label'],
                    label_text=N_("YouTube player version"),
                    validator=Int,
                ),
                RadioButtonList('iv_load_policy',
                    options=lambda: (
                        (1, _('Show video annotations by default.')),
                        (3, _('Hide video annotations by default.')),
                    ),
                    css_label_classes=['container-list-label'],
                    label_text=N_("Video annotations"),
                    validator=Int,
                ),
                CheckBox('disablekb', label_text=N_('Disable the player keyboard controls.'),
                    help_text=N_('Not supported by HTML5 player.')),
                CheckBox('autoplay', label_text=N_('Autoplay the video when the player loads.')),
                CheckBox('modestbranding', label_text=N_('Do not show YouTube logo in the player controls'), 
                    help_text=N_('Not supported by AS2 player.')),
                CheckBox('fs', label_text=N_('Display fullscreen button.')),
                CheckBox('hd', label_text=N_('Enable high-def quality by default.'), 
                    help_text=N_('Applies only for the AS2 player, the AS3 player will choose the most appropriate version of the video version (e.g. considering the user\'s bandwidth)')),
                CheckBox('rel', label_text=N_('Display related videos after playback of the initial video ends.')),
                CheckBox('showsearch', label_text=N_('Show the search box when the video is minimized. The related videos option must be enabled for this to work.'),
                    help_text=N_('AS2 player only')),
                CheckBox('showinfo', label_text=N_('Display information like the video title and uploader before the video starts playing.')),
                CheckBox('wmode', label_text=N_('Enable window-less mode (wmode)'), 
                    help_text=N_('wmode allows HTML/CSS elements to be placed over the actual Flash video but requires more CPU power.')),
                RadioButtonList('autohide',
                    options=lambda: (
                        (0, _('Always show player controls.')),
                        (1, _('Autohide all player controls after a video starts playing.')),
                        (2, _('Autohide only the progress bar after a video starts playing.')),
                    ),
                    css_label_classes=['container-list-label'],
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
