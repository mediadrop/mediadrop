.. _dev_controllers_public:

==================
Public Controllers
==================

MediaDrop provides a robust frontend, but if it does not suit your needs you
can easily revise it or even completely replace it, while still maintaining the
benefits of MediaDrop's admin interface.

A listing of the public-facing controller methods is below. See the
`mediacore/config/routing.py` file for information on the URLs that point to
these methods.


Browsing/Viewing Media
----------------------

.. automodule:: mediacore.controllers.media

.. autoclass:: MediaController
   :members:
   :undoc-members:


Browsing Podcasts
-----------------

.. automodule:: mediacore.controllers.podcasts

.. autoclass:: PodcastsController
   :members:
   :undoc-members:


Uploading Videos
----------------

.. automodule:: mediacore.controllers.upload

.. autoclass:: UploadController
   :members:
   :undoc-members:


XML Sitemaps
------------

.. automodule:: mediacore.controllers.sitemaps

.. autoclass:: SitemapsController
   :members:
   :undoc-members:


Error Messages
--------------

.. automodule:: mediacore.controllers.error

.. autoclass:: ErrorController
   :members:
   :undoc-members:

