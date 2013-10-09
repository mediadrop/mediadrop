.. _user_admin_settings:

========================
Settings Admin Interface
========================

Analytics
---------
Tracking code should be in the format UA-xxxx-xx. See the
`Google site <http://www.google.com/support/googleanalytics/bin/answer.py?answer=55603>`_
for help.

Leave the tracking code blank to disable Google Analytics.


Categories
----------
Categories, in MediaDrop, are created by the admins to represent whatever
categorization scheme they wish to employ.

Like Tags, Categories are considered when searching for media and when
displaying related media.

Unlike Tags, Categories have their own section in the frontend that that
provides a way for users to browse the available Categories, and to explore
the media in each Category.

Categories can be nested. A parent category is considered to contain all of
the media contained by its child categories.

Each Media item can belong to any number of categories.

The Categories for each Media item must be assigned by administrators, there
is no way for users using the frontend upload form to set Categories.


Comments
--------
If Akismet is enabled, spam will be discarded before saving it for moderator
approval.

In order to enable Akismet anti-spam protection, you must sign up for an
Akismet API key at the Akismet website.

Enable Akismet anti-spam protection by entering your API key in this form.

The Akismet URL should be set to the 'blog url' you signed up with. If left
empty, this will default to your application root URL.


Display
-------
*Rich Text Editing:*

The use of TinyMCE is not strictly XHTML compliant, but it works in
FireFox >= 1.5, Safari >= 3, Internet Explorer >= 5.5. A user's browser must
have JavaScript enabled in order to use TinyMCE. If JavaScript is not enabled,


*Player Selection--Theoretical Background:*

All audio and video files can be characterized by two features:

1. The container format, which determines how the data is organized within
   the file.
2. The codecs, which determine how your audio or video is represented as data
   for the computer.

Often, particular container formats are closely coupled with codecs. For
instance, if one were to see a .m4a file, one could fairly safely assume that
it used a XXX container format, and contained audio data encoded by a XXX
codec.

Audio and Video can be played via HTML5 in some browsers if the browser
supports the container format and codecs used in the media file.

Audio and Video can be played via Flash in some browsers if Flash
supports the container format and codecs used in the media file, and if the
browser, in turn, supports Flash.

MediaDrop has a built in list of which browsers support Flash, which containers
and codecs Flash supports, and which containers and codecs are supported by
which browsers through HTML5.

MediaDrop also has built in logic that will guess the container format and
applicable codecs for a given media file based on its filename.

Together, this means that if you have multiple audio or video files attatched
to a Media object, MediaDrop can take into account the capabilities of your
users' browsers, the available files, and your (the admin's) player
preferences, and serve the best combination of files and players to each
user, individually.


*Player Selection--Consequences:*

A useable Flash player will be found if:
   1. the user's browser supports Flash
   2. and there is a media file associated with the media object that Flash is
      capable of playing.

A useable HTML5 player will be found if:
   1. the user's browser supports the HTML5 <video> tag
   2. there is a media file associated with the media object that
      the user's browser is capable of playing natively.

Adobe published a list of which `formats Flash supports <http://kb2.adobe.com/cps/402/kb402866.html>`_.

For HTML5 there is also a list of `which browsers support which formats <http://diveintohtml5.com/video.html#what-works>`_ natively.

In the case that an embedded video (YouTube/Vimeo/etc.) the appropriate media
file for a media object, that video will be displayed within the selected
Flash or HTML5 player, if possible.

When choosing which media file to display, the following criteria are applied
(in order of importance):

   1. Video will be preferred over Audio
   2. Files that will play in the preferred player get priority.
   3. Embedded files (YouTube/Vimeo/etc.) get priority.
   4. Larger filesizes get priority.

Regardless of what the "Preferred Media Player Type" setting is, if the chosen
setting will yield no useable player for a particular user's browser, an
error message will be displayed to the user in place of the media object.
The exception to this is if the media object has an embedded
(YouTube/Vimeo/etc.) media file, in which case MediaDrop will attempt to
render this embedded file, rather than display an error, leaving it up to the
embedded player to display an error if necessary.


Notifications
-------------
For each action (Media Uploaded, Comment Posted, Support Requested), you can
set a comma-separated list of email addresses to notify when they occur.

Leave a field blank to disable notifications for that event.

The 'Send Emails From' field must be a valid email address.


Popularity
----------
MediaDrop uses a popularity ranking algorithm similar to Reddit's. The
popularity of a Media item can be described by the equation:

.. sourcecode:: text

   popularity_points = log_X(media.likes) + media.age/Y

Where:

* *X* (the base of the logarithm, in this equation) is the
  "Popularity Decay Exponent"
* *Y* is the "Popularity Decay Lifetime"
* *media.age* is the number of hours between January 1, 2000, and the time the
  media item was published
* *media.likes* is the number of 'like' votes the media item has received from
  users

Essentially, in this algorithm, a media item *(A)* that is *Y* hours older than
media item *(B)*, will need *X* times as many votes as *(B)* to rank at the same
level.

Lower traffic websites will want a higher *Y* value, or a lower *X* value, or both.


Tags
----
Tags are keywords or terms that can be used to describe a Media item. They could describe content, history, author, format, your personal opiions, anything at all about a Media item. Each Media item can have an unlimited number of tags.

Like Categories, they are considered when searching for media and when
displaying related media.

Unlike Categories, Tags do not have much of an interface presence in the
frontend. Tags can also be suggested by users when uploading their own videos
through the frontend upload interface.

It is generally assumed that you will use tags more liberally than categories
when describing media files.

Tags are also used to generate the <meta keywords="..."> on media pages, to
make your website friendlier for search engines.


Upload
------

*Thumbnails:*

When adding media that is being hosted on YouTube, Vimeo, or a similar platform,
MediaDrop will automatically fetch the Title and Duration of the media item
from the appropriate website. Furthermore, MediaDrop can be configured to
automatically fetch the thumbnail images from these services, in the event
that you have not already specified a thumbnail image for the Media item.

*Remote Storage:*

MediaDrop has built-in support for FTP transfers, so that you can
automatically store your media on an FTP server, while allowing your users to
perform their uploads through MediaDrop.

In addition to the FTP server address, subdirectory,  username, and password,
you will have to configure the HTTP URL from which the media files can later
be downloaded.

For example, it is a common setup to upload to a "public_files" directory on an
FTP server at "ftp.myhost.com" and then have the files be accessible through a
URL like "http://myhost.com/myuser/".

In this release of MediaDrop, only remote HTTP hosting is available: RTMP is
unsupported.


Users
-----

MediaDrop's users interface is pretty simple right now. You can add any number
of administrator users you like.
