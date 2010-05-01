.. _dev_api:

===============
Third-Party API
===============

.. module:: mediacore.controllers.media_api

MediaCore provides a simple API for grabbing media info via HTTP.


Exposed Media Info
------------------

Whether querying for a list or for a single media item, the following
information is returned:

    id
        The :attr:`mediacore.model.media.Media.id`
    slug
        The :attr:`mediacore.model.media.Media.slug`
    url
        The permalink
    title
        The :attr:`mediacore.model.media.Media.title`
    type
        The :attr:`mediacore.model.media.Media.type` (audio or video)
    podcast
        The :attr:`mediacore.model.podcasts.Podcast.slug` this
        media has been published under, if any
    description
        The :attr:`mediacore.model.media.Media.description` in XHTML
    description_plain
        The :attr:`mediacore.model.media.Media.description_plain` in
        plain text
    comment_count
        The number of published comments so far
    publish_on
        The date of publishing, eg. "2010-02-16 15:06:49"
    likes
        The :attr:`mediacore.model.media.Media.likes`
    views
        The :attr:`mediacore.model.media.Media.views`
    thumbs
        A dict of dicts containing URLs, width and height of
        different sizes of thumbnails. The default sizes
        are 'ss', 's', 'm' and 'l'. Using medium for example::

            medium_url = thumbs['m']['url']
            medium_width = thumbs['m']['x']
            medium_height = thumbs['m']['y']

In addition, the :meth:`get` action returns an 'embed' property
with the XHTML necessary to embed the audio/video player on your
on your site.


Querying for a Media List
-------------------------

.. automethod:: MediaApiController.index


Fetching a single Media item
----------------------------

.. automethod:: MediaApiController.get
