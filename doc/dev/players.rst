.. _dev_players:

=================
Media Players API
=================

MediaDrop was designed to make it straightforward to fully integrate new
audio/video players into the display system.

While MediaDrop supports 9 Flash and/or HTML5 players out of the box (including
the popular JWPlayer, Flowplayer, and Sublime Video Players, as well as several
players customized to display embedded material from third-party websites), we
recognize that some users may want to incorporate different players.

To this end, we have designed the playback system around a well-defined API.
All of MediaDrop's default players implement this API.


.. automodule:: mediacore.lib.players

Summary
-------

Players have 3 parts.

1. A Python class that implements the
   :class:`mediacore.lib.players.AbstractPlayer` abstract class,
2. A Genshi template (all players use the same template,
   :file:`mediacore/templates/players/html5_or_flash.html`;
   its use is defined in :func:`mediacore.lib.players.media_player`),
3. A JavaScript manager class, written using Google's :ref:`closure <dev_closure>`
   library, that inherits from :obj:`goog.ui.Component` and is responsible for
   handling player interactions (resizes, clicks, etc.).

When a :class:`Media <mediacore.model.media.Media>` object is selected to be
rendered, a list of :class:`StorageURIs <mediacore.lib.uri.StorageURI>`
is generated from that object's
:attr:`MediaFiles <mediacore.model.media.Media.files>`. Each enabled
:class:`Player <mediacore.lib.players.AbstractPlayer>` is then
asked, in order, if it can use any of the available StorageURIs. The first
Player that can play one of the StorageURIs is rendered. This logic is
contained in :func:`mediacore.lib.players.media_player`.

Players can optionally define a dict of editable properties in their
:attr:`default_data <mediacore.lib.players.AbstractPlayer.default_data>`
dict if they also provide a subclass of
:class:`mediacore.forms.admin.players.PlayerPrefsForm` whose
:meth:`display <mediacore.forms.admin.players.PlayerPrefsForm.display>` and
:meth:`save_data <mediacore.forms.admin.players.PlayerPrefsForm.save_data>`
methods can map the form values to and from the data dict. Players that
do this will have links, in MediaDrop's admin backend, to a page where an admin
can use the rendered form to edit the Player instance. An example of a player
that has this feature is :class:`mediacore.lib.players.YoutubeFlashPlayer`.


Implementation - Python
-----------------------

Any new player class will need to be imported and registered like so:

.. sourcecode:: python

   from mediacore.lib.players import AbstractPlayer

   class MyPlayer(AbstractPlayer):
       """
       Implement all abstract properties and abstract methods here ...
       """

   AbstractPlayer.register(MyPlayer)

See the players in :file:`mediacore/lib/players.py` for examples.


Implementation - JavaScript
---------------------------

Developers should familiarize themselves with MediaDrop's :ref:`dev_closure`
guide and the library class
`goog.ui.Component <http://code.google.com/p/closure-library/wiki/IntroToComponents>`_.

Every Player has a JavaScript class that is responsible for handling the
decoration and resizing of the player element in the page.
It is this class that is instantiated using the code produced by
:meth:`render_js_player <AbstractPlayer.render_js_player>`.

This managing class inherits from :obj:`goog.ui.Component`.
It must implement the MediaDrop-specific :meth:`getSize` and :meth:`setSize`.

See the files in :file:`mediacore/public/scripts/mcore/players/` for examples.


Abstract Base Class
-------------------

.. autoclass:: AbstractPlayer
   :members:

   .. automethod:: __init__

Player Preferences Form
-----------------------

.. autoclass:: mediacore.forms.admin.players.PlayerPrefsForm
   :members:

Related Functions
-----------------

.. autofunction:: media_player
