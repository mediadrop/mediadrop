.. _dev_api:

========
JSON API
========

MediaDrop provides a simple API for grabbing media info. A GET request to any
of the public methods on this page will return a JSON object with the returned
information.

MediaDrop's controllers render JSON objects by preparing what we call a
JSON-ready dict. In these dicts, all keys are Python's unicode type and all
values are of a type in the table below. There there is a 1-1 mapping between
Python types and JavaScript types:

   ======= ==========
   Python  JavaScript
   ======= ==========
   dict    Object
   list    Array
   unicode String
   int     Number
   float   Number
   bool    Boolean
   None    null
   ======= ==========

**API KEYS**: It is up to the administrator of a MediaDrop site to allow or
disallow public access to that site's API. To this end, an administrator can
choose to require an API Key be sent with every API request. This key is
configurable in MediaDrop's *Admin -> Settings -> Data API* page.


.. automodule:: mediacore.controllers.api.media

Querying Media Items
--------------------


MediaDrop provides a
:meth:`get <mediacore.controllers.api.media.MediaController.get>`
method for returning information about an individual media item (given an
*id* or *slug*) and an
:meth:`index <mediacore.controllers.api.media.MediaController.index>`
method for returning information on a list of  media items that match
specified criteria.

Both of these methods make use of the **media_info** dicts provided by the
private :meth:`_info <mediacore.controllers.api.media.MediaController._info>`
method.

.. automethod:: MediaController._info

Single Media Items
~~~~~~~~~~~~~~~~~~

If you know the :attr:`id <mediacore.model.media.Media.id>` or
:attr:`slug <mediacore.model.media.Media.slug>` of a single media item you want to
query, use the :meth:`get <mediacore.controllers.api.media.MediaController.get>`
method (available by default at **/api/media/get**).

Examples:

- Get info for media item with ID 24
      http://demo.getmediacore.com/api/media/get?id=24&api_key=zPDyJXdjrPgmFxHC1xw
- Get info for media item with slug 'the-seed'
      http://demo.getmediacore.com/api/media/get?slug=the-seed&api_key=zPDyJXdjrPgmFxHC1xw

.. automethod:: MediaController.get


Lists of Media Items
~~~~~~~~~~~~~~~~~~~~

To return a filtered list of media info, use the
:meth:`index <mediacore.controllers.api.media.MediaController.index>`
method (available by default at **/api/media**).

Examples:

- Get info for the 10 latest videos
      http://demo.getmediacore.com/api/media?type=video&api_key=zPDyJXdjrPgmFxHC1xw
- Get info for the first 20 media published in February, 2011
      http://demo.getmediacore.com/api/media?limit=20&published_after=2011-02-01%2000:00:00&published_before=2011-03-01%00:00:00&api_key=zPDyJXdjrPgmFxHC1xw

.. automethod:: MediaController.index


Querying Media Files
--------------------

MediaDrop provides a
:meth:`files <mediacore.controllers.api.media.MediaController.files>`
method for returning information about the
:class:`mediacore.model.media.MediaFile` instances associated with a given
:class:`mediacore.model.media.Media` instance.

This method makes use of the **file_info** dicts provided by the private
:meth:`_file_info <mediacore.controllers.api.media.MediaController._file_info>`
method.

.. automethod:: MediaController._file_info


Lists of Media Files
~~~~~~~~~~~~~~~~~~~~

When you know the :attr:`id <mediacore.model.media.Media.id>` or
:attr:`slug <mediacore.model.media.Media.slug>` of a single
:class:`media <mediacore.model.media.Media>`
instance that you want to get the file info for,
:meth:`files <mediacore.controllers.api.media.MediaController.files>`
method (available by default at **/api/media/files**).

Examples:

- Get info on media files for media item with ID 24
      http://demo.getmediacore.com/api/media/files?id=24&api_key=zPDyJXdjrPgmFxHC1xw
- Get info on media files for media item with slug 'the-seed'
      http://demo.getmediacore.com/api/media/files?slug=the-seed&api_key=zPDyJXdjrPgmFxHC1xw

.. automethod:: MediaController.files



.. automodule:: mediacore.controllers.api.categories

Querying Categories
-------------------

MediaDrop provides two methods of listing categories:
:meth:`index <mediacore.controllers.api.categories.CategoriesController.index>`
for listing all categories in a flat list, and
:meth:`tree <mediacore.controllers.api.categories.CategoriesController.tree>`
for listing all categories in the hierarchy tree.

Both of these methods make use of the **category_info** dicts provided by the
private
:meth:`_info <mediacore.controllers.api.categories.CategoriesController._info>`
method.

.. automethod:: CategoriesController._info


Lists of Categories
~~~~~~~~~~~~~~~~~~~

To query a flat list of categories, use the
:meth:`index <mediacore.controllers.api.categories.CategoriesController.index>`
method (available by default at **/api/categories**).

Examples:

- List the first 50 categories
      http://demo.getmediacore.com/api/categories?api_key=zPDyJXdjrPgmFxHC1xw
- List the second group of 10 categories, in alphabetical order
      http://demo.getmediacore.com/api/categories?order=name%20asc&offset=10&limit=10&api_key=zPDyJXdjrPgmFxHC1xw

.. automethod:: CategoriesController.index


Hierarchies of Categories
~~~~~~~~~~~~~~~~~~~~~~~~~

To query a hierarchy of categories, use the
:meth:`tree <mediacore.controllers.api.categories.CategoriesController.tree>`
method (available by default at **/api/categories/tree**).

Examples:

- Get a hierarchy of all categories:
      http://demo.getmediacore.com/api/categories/tree?api_key=zPDyJXdjrPgmFxHC1xw
- Get a nested list of categories that are children of 'short-film'
      http://demo.getmediacore.com/api/categories/tree?slug=short-film&api_key=zPDyJXdjrPgmFxHC1xw

.. automethod:: CategoriesController.tree


Python Example
--------------

The following Python code fetches the first 6 videos published in February,
2011, and outputs a simple HTML snippet with a thumbnail, title, link, and
short description of each video.

.. sourcecode:: python

   import urllib
   try:
      import json # py26
   except:
      import simplejson as json # py25 and under

   api_url = 'http://demo.getmediacore.com/api/media'
   api_key = 'zPDyJXdjrPgmFxHC1xw'
   excerpt_length = 180

   def fetch_media_list(**kwargs):
      kwargs['api_key'] = api_key
      querystring = urllib.urlencode(kwargs)
      f = urllib.urlopen(api_url + '?' + querystring)
      return json.loads(f.read())

   def truncate(text):
      if len(text) > excerpt_length:
         right = text[:excerpt_length].rindex(' ')
         text = text[:right] + '&hellip;'
      return text

   result = fetch_media_list(
      type='video',
      published_after='2011-02-01 00:00:00',
      limit=6
   )
   videos = result['media']

   output = ["<h1>Previews:</h1>"]

   for v in videos:
      output.append(
         '<div><a href="%s"><img src="%s" alt="%s"/>%s</a>%s</div>' % (
            v['url'], v['thumbs']['s']['url'], v['title'], v['title'],
            truncate(v['description_plain'])
         )
      )

   print '\n'.join(output)


PHP Example
-----------

The following PHP code fetches the first 6 videos published in February,
2011, and outputs a simple HTML snippet with a thumbnail, title, link, and
short description of each video.

.. sourcecode:: php

   <?php
      $media_api = 'http://demo.getmediacore.com/api/media';
      $api_key = 'zPDyJXdjrPgmFxHC1xw';
      $excerpt_length = 180;

      function fetch_media_list($data) {
         global $media_api, $api_key;

         $data['api_key'] = $api_key;
         $uri = $media_api . '?' . http_build_query($data);
         return json_decode(file_get_contents($uri));
      }

      function truncate($text) {
         global $excerpt_length;

         if (strlen($text) > $excerpt_length) {
            $left = 0;
            $right = strrpos(substr($text, 0, $excerpt_length-1), ' ');
            $text = substr($text, $left, $right) . '&hellip;';
         }
         return $text;
      }

      $result = fetch_media_list(array(
         'type' => 'video',
         'published_after' => '2011-02-01%2000:00:00',
         'limit' => 6
      ));
      $videos = $result->media;
   ?>

   <h1>Previews:</h1>
   <?php foreach ($videos as $video): ?>
      <div>
         <a href="<?php echo $video->url; ?>">
            <img src="<?php echo $video->thumbs->s->url; ?>"
                alt="<?php echo $video->title; ?>" />
            <?php echo $video->title; ?>
         </a>
         <?php echo truncate($video->description_plain); ?>
      </div>
   <?php endforeach ?>

