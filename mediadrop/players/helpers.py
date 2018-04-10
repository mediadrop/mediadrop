# -*- coding: utf-8 -*-
# This file is a part of MediaDrop (https://www.mediadrop.video),
# Copyright 2009-2018 MediaDrop contributors
# For the exact contribution history, see the git revision log.
# The source code contained in this file is licensed under the GPLv3 or
# (at your option) any later version.
# See LICENSE.txt in the main project directory, for more information.

from itertools import izip

from genshi.builder import Element

from mediadrop.lib.templating import render
from mediadrop.lib.util import url_for


__all__ = [
    'embed_iframe',
    'embed_player',
    'media_player',
    'pick_any_media_file',
    'pick_podcast_media_file',
    'preferred_player_for_media',
    'update_enabled_players',
]

def preferred_player_for_media(media, **kwargs):
    uris = media.get_uris()

    from mediadrop.model.players import fetch_enabled_players
    # Find the first player that can play any uris
    for player_cls, player_data in fetch_enabled_players():
        can_play = player_cls.can_play(uris)
        if any(can_play):
            break
    else:
        return None

    # Grab just the uris that the chosen player can play
    playable_uris = [uri for uri, plays in izip(uris, can_play) if plays]
    kwargs['data'] = player_data
    return player_cls(media, playable_uris, **kwargs)


def media_player(media, is_widescreen=False, show_like=True, show_dislike=True,
                 show_download=False, show_embed=False, show_playerbar=True,
                 show_popout=True, show_resize=False, show_share=True,
                 js_init=None, **kwargs):
    """Instantiate and render the preferred player that can play this media.

    We make no effort to pick the "best" player here, we simply return
    the first player that *can* play any of the URIs associated with
    the given media object. It's up to the user to declare their own
    preferences wisely.

    Player preferences are fetched from the database and the
    :attr:`mediadrop.model.players.c.data` dict is passed as kwargs to
    :meth:`AbstractPlayer.__init__`.

    :type media: :class:`mediadrop.model.media.Media`
    :param media: A media instance to play.

    :param js_init: Optional function to call after the javascript player
        controller has been instantiated. Example of a function literal:
        ``function(controller){ controller.setFillScreen(true); }``.
        Any function reference can be used as long as it is defined
        in all pages and accepts the JS player controller as its first
        and only argument.

    :param \*\*kwargs: Extra kwargs for :meth:`AbstractPlayer.__init__`.

    :rtype: `str` or `None`
    :returns: A rendered player.
    """
    player = preferred_player_for_media(media, **kwargs)
    return render('players/html5_or_flash.html', {
        'player': player,
        'media': media,
        'uris': media.get_uris(),
        'is_widescreen': is_widescreen,
        'js_init': js_init,
        'show_like': show_like,
        'show_dislike': show_dislike,
        'show_download': show_download,
        'show_embed': show_embed,
        'show_playerbar': show_playerbar,
        'show_popout': show_popout,
        'show_resize': show_resize and (player and player.supports_resizing),
        'show_share': show_share,
    })

def pick_podcast_media_file(media):
    """Return a file playable in the most podcasting client: iTunes.

    :param media: A :class:`~mediadrop.model.media.Media` instance.
    :returns: A :class:`~mediadrop.model.media.MediaFile` object or None
    """
    from .itunes import iTunesPlayer
    uris = media.get_uris()
    for i, plays in enumerate(iTunesPlayer.can_play(uris)):
        if plays:
            return uris[i]
    return None

def pick_any_media_file(media):
    """Return a file playable in at least one of the configured players.

    :param media: A :class:`~mediadrop.model.media.Media` instance.
    :returns: A :class:`~mediadrop.model.media.MediaFile` object or None
    """
    uris = media.get_uris()
    from mediadrop.model.players import fetch_enabled_players
    for player_cls, player_data in fetch_enabled_players():
        for i, plays in enumerate(player_cls.can_play(uris)):
            if plays:
                return uris[i]
    return None

def update_enabled_players():
    """Ensure that the encoding status of all media is up to date with the new
    set of enabled players.

    The encoding status of Media objects is dependent on there being an
    enabled player that supports that format. Call this method after changing
    the set of enabled players, to ensure encoding statuses are up to date.
    """
    from mediadrop.model import DBSession, Media
    media = DBSession.query(Media)
    for m in media:
        m.update_status()

def embed_iframe(media, width=400, height=225, frameborder=0, **kwargs):
    """Return an <iframe> tag that loads our universal player.

    :type media: :class:`mediadrop.model.media.Media`
    :param media: The media object that is being rendered, to be passed
        to all instantiated player objects.
    :rtype: :class:`genshi.builder.Element`
    :returns: An iframe element stream.

    """
    src = url_for(controller='/media', action='embed_player', slug=media.slug,
                  qualified=True)
    tag = Element('iframe', src=src, width=width, height=height,
                  frameborder=frameborder, **kwargs)
    # some software is known not to work with self-closing iframe tags 
    # ('<iframe ... />'). Several WordPress instances are affected as well as
    # TWiki http://mediadrop.video/community/topic/embed-iframe-closing-tag
    tag.append('')
    return tag

embed_player = embed_iframe
