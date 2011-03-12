.. _dev_plugins:

===========
Plugins API
===========

As of version 0.9.0, MediaCore defines methods for hooking into events
and for creating extra functionality. A simple plugin might add a new
:class:`mediacore.lib.StorageEngine`. A more complex one might define a new set
of models or a new controller and use the Events system and extra templates to
extend the existing actions of MediaCore to add completely new functionality.

While there is not yet official documentation for MediaCore's plugins API (it's
coming!) Felix Schwarz, an active member of the MediaCore community, has written
a good introduction to the system for people that would like to get started
right away.

See Felix's examples at:
`<http://schwarz.eu/oss/wiki/2011/03/mediacore-%E2%80%93-an-extensible-video-platform>`_.

Felix is one of our most active community developers. He has been a great help
to the MediaCore development team with his code contributions, documentation,
and insights.

Thanks Felix!
