.. _user_admin_settings:

========================
Settings Admin Interface
========================

Analytics
---------
* Tracking code is in the format UA-xxxx-xx. See the `Google site <http://www.google.com/support/googleanalytics/bin/answer.py?answer=55603>`_ for help.
* Leave blank to disable Google Analytics.

Categories
----------
* Categories, as the name implies, provide a concise list of the main categories of media on your site. Like Tags, they are considered when searching for media and when displaying related media. Unlike Tags, Categories have their own section in the front-end that that provides a way for users to explore the media by subject matter.
* Categories can be nested. A parent category is considered to contain all of the media contained by its child categories.


Comments
--------
* Enable akismet anti-spam protection by setting your API key.
* The Akismet URL is the 'blog url' you signed up with. This defaults to your application root, if empty.
* If Akismet is enabled, spam will be discarded before saving it for moderator approval.



Display
-------
* Use of TinyMCE is not strictly XHTML compliant, but works in FF>=1.5, Safari>=3, IE>=5.5, so long as javascript is enabled.
* Regardless of the "Preferred Media Player Type" setting, if the chosen setting will yield no useable player for a particular user's browser, an error message will be displayed to the user in place of the media object. The exception to this is if the media object has an embedded (YouTube/Vimeo/etc.) media file, in which case MediaCore will attempt to render this embedded file, rather than display an error, leaving it up to the embedded player to display an error if necessary.
* A useable Flash player will be found if the user's browser supports Flash, and there is a media file associated with the media object that Flash is capable of playing. A list of which formats Flash supports can be found `here <http://kb2.adobe.com/cps/402/kb402866.html>`_.
* A useable HTML5 player will be found if the user's browser supports the HTML5 <video> tag, and there is a media file associated with the media object that the user's browser is capable of playing natively. A list of which browsers support which formats natively can be found `here <http://diveintohtml5.com/video.html#what-works>`_.
* In the case that an embedded video (YouTube/Vimeo/etc.) the appropriate media file for a media object, that video will be displayed within the selected Flash or HTML5 player, if possible.
* When choosing which media file to display, the following criteria are applied (in order of importance):

  1. Files that will play in the preferred player get priority.
  2. Embedded files (YouTube/Vimeo/etc.) get priority.


Notifications
-------------
* Where should MediaCore send an email when the following actions occur?
* Email fields may be comma separated lists of email addresses.
* Leave blank for no notification.


Popularity
----------
* MediaCore uses a popularity ranking algorithm similar to Reddit's.
* The popularity of a media item is described by: log_x(media.likes) + media.age/y
* Where:

  * x (the base of the logarithm) is the "Popularity Decay Exponent"
  * y is the "Popularity Decay Lifetime"
  * media.age is the number of hours between January 1, 2000, and the time the media item was published
  * media.likes is the number of likes the media item has received

* Essentially, in this algorithm, a media item (A) that is y hours older than media item (B), will need x times as many votes as (B) to rank at the same level.
* Lower traffic websites will want a higher y value, or a lower x value, or both.

Tags
----
* Tags are keywords or terms that describe each media item. Like Categories, they are considered when searching for media and when displaying related media. Unlike Categories, Tags are mostly invisible to the user, though Tags are used to generate the <meta keywords="..."> tags on media pages.

Upload
------
* Use the FTP options below if you want to store media files on a CDN instead of storing them locally.
* In this release of MediaCore, only remote HTTP hosting is available: RTMP is unsupported.
* Thumbnails will only ever be fetched from YouTube, Vimeo, etc. if the embedded video is the first media file added to a particular media item.

Users
-----
* Nothing yet?
