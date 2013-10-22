.. _dev_plugins:

===========
Plugins API
===========

As of version 0.9.0, MediaDrop defines methods for hooking into events
and for creating extra functionality. A simple plugin might add a new
:class:`mediacore.lib.StorageEngine`. A more complex one might define a new set
of models or a new controller and use the Events system and extra templates to
extend the existing actions of MediaDrop to add completely new functionality.

While there is not yet official documentation for MediaDrop's plugins API (it's
coming!) Felix Schwarz, an active member of the MediaDrop community, has written
a good introduction to the system for people that would like to get started
right away.

See Felix's examples at:
`<http://schwarz.eu/oss/wiki/2011/03/mediacore-%E2%80%93-an-extensible-video-platform>`_.

Felix is one of our most active community developers. He has been a great help
to the MediaDrop development team with his code contributions, documentation,
and insights.

Thanks Felix!


====================
Ecoding Installation
====================

Pre Requisites: Please make sure you have installed the Encoding plugin and
created a cloud on `pandastream.com <http://pandastream.com/>`_ with
your Panda Stream account.


**1. Create MediaDrop Storage Engine**

Login into your MediaDrop admin panel, and go to Settings > Storage Engines.
Click Add New engine > Panda Transcoding and Storage. You can also select which
encoding profiles you want to include.


**2. Panda Storage Engine Fields**

Display Name, recommended to leave it as it is.


**3. Panda Account Details**

- Cloud ID
        Login to your PandaStream account, and at the dashboard click on your cloud.
        On the Cloud dashboard, you'll see the name of your cloud and the ID. This ID
        is what you are after for this field.

- Access Key / Secret Key
        This is your PandaStream API Access Key. Login into PandaStream, and click
        on API Access.


**4. Amazon S3 Info**

You need an S3 bucket to save your videos to. Enter the name of your Bucket
when creating your Panda Stream Encoding Cloud. You can also enter any
CloudFront domains you may have as well. After saving this information you
can then go back and select what you want.
