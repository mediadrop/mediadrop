.. _user_admin_media:

================================
Media Management Admin Interface
================================

A good first resource for media management is the
`MediaCore CE Workflow Video <http://static.mediadrop.net/files/videos/tutorial-workflow-in-mediacore.mp4>`_.


Files
-----
Any number of files can be uploaded in association with a Media item.
MediaDrop will automatically decide which file(s), from the ones available,
should be served to a particular user.

It is assumed that all associated files are representations of the same
content, be they Video files, Audio files, or Closed Captioning files.

If a Media item has associated Audio files, but has no associated Video files,
the Media item will be assumed to be an audio-only Media item, and MediaDrop
will attempt to serve the highest bitrate Audio file available, in a format
that the requesting client can listen to.

If a Media item has associated Video files, it will be assumed to be,
primarily, a video Media item, and MediaDrop will attempt to serve the
highest bitrate Video file available in a format that the requesting client
can listen to.

If a Media item has associated Video files and Audio files, the Audio files
will be assumed to be audio descriptions of the video file. If the selected
player (see Display Settings documentation) supports audio descriptions,
MediaDrop will provide the client with both the video and the audio
description. This is one of the ways that MediaDrop provides accessibility
for visually impaired users.

Users can upload `Timed Text <http://www.w3.org/TR/ttaf1-dfxp/>`_ .xml files to
be used for closed captioning. This works in much the same way as audio
descriptions.


Status
------

A Media item must go through three distinct stages, in MediaDrop, before it is
published. All of these stages can be managed through the Media Edit interface.

1. It must be reviewed.

   This means that an administrator has seen and approved the content.
   Review is accomplished by clicking the 'Review Complete' button.

2. It must be encoded in a useable format.

   In general, this means any normal web format (.flv, .mp4, .mp3, etc.),
   however if a Media item is designated to be served as a Podcast, it must
   have an associated .mp3, .mp4, .m4a, or .m4v file. Furthermore, if the
   selected media player is HTML5 only, there must be an available
   OGG/Theora (.ogg), MP4 (.mp4, .m4a, .m4v), .mp3, or .webm file.

3. It must be published.

   This can be accomplished by clicking 'Publish Now' to publish immediately,
   or by clicking on the current publish date, or the word 'pending' in the
   Publish Status box, and selecting a date in the future from the dropdown
   calendar.

