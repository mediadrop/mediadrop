.. _dev_storage:

=================
Media Storage API
=================

There are many, many ways to host media on the Internet. MediaDrop supports a
bunch of them right out-of-the-box, but we wanted to make it simple to add
support for new methods.

By default, MediaDrop supports hosting media files:

* on third-party services (like blip.tv, Dailymotion, Google video, Vimeo, YouTube)
* via any direct HTTP, HTTPS, or RTMP url to a media file
* locally, by serving uploaded files via the same webserver as MediaDrop

MediaDrop can also automatically transfer uploaded media files to a
remote FTP server, if that FTP server makes the files available at an HTTP url.

All of these options are implemented using MediaDrop's Storage Engine API.
This API is designed to make it simple for new storage methods to be added.

The Storage Engine system is located in :mod:`mediacore.lib.storage` and the
API is defined by the abstract class
:class:`mediacore.lib.storage.StorageEngine`.
Most of MediaDrop's own StorageEngines inherit from the helpful subclasses
:class:`mediacore.lib.storage.FileStorageEngine` and
:class:`mediacore.lib.storage.EmbedStorageEngine`.
Forms associated with StorageEngines all inherit from
:class:`mediacore.forms.admin.storage.StorageForm`.


Summary
-------

There are three components in MediaDrop's file storage system:
:class:`StorageEngines <mediacore.lib.storage.StorageEngine>`,
:class:`MediaFiles <mediacore.model.media.MediaFile>`, and
:class:`StorageURIs <mediacore.lib.uri.StorageURI>`.
Each MediaFile object represents a unique file somewhere in cyberspace.
Each URI represents a method and address via which that file might be accessed.

StorageEngine classes define the logic for storing and deleting media files and
for listing all of the URIs via which those files might be accessed. For
example, the :class:`mediacore.lib.storage.ftp.FTPStorage` class handles the
logic for storing/deleting an uploaded file on a remote FTP server, and the
logic for generating an HTTP URL at which the stored media can be accessed. It
also defines a dictionary of settings and a form for editing those settings.
On the other hand, a StorageEngine like
:class:`mediacore.lib.storage.youtube.YoutubeStorage`
contains the logic for parsing YouTube URLs, fetching thumbnails and
descriptions from YouTube, and generating the information required to embed a
YouTube video in a page. It defines no form, because it has no settings.

Because different StorageEngines will need to keep different data about the
MediaFiles that they own, MediaFiles have a flexible
:attr:`unique_id <mediacore.model.media.MediaFile.unique_id>`
attribute that the owning StorageEngine is responsible for populating and reading.
Some StorageEngines use this field to store a serialized dict, some store a
single ID number or even simply an HTTP URL.

When called upon to be used, a MediaFile may be asked to return all of the URIs
via which it is accessible. For example, a file stored on Amazon S3 may be
accessible via HTTP or RTMP, while a file stored locally may be accessible via a
HTTP url or via local file path. The StorageEngine that owns the MediaFile is
responsible for generating with this list.  URIs are not stored in the
database, but are generated at request time based on the properties of the
involved MediaFile and StorageEngine.


Internal Process
----------------

When a new MediaFile is being added to MediaDrop (for example, via the admin
Add New Media form, or via the front-end Upload form), it may come as the
result of a populated file input (e.g. an uploaded MP4 file), or a populated
text input (e.g. a YouTube URL).

MediaDrop will attempt to find the most appropriate StorageEngine to handle the
given file/string combo. To find an appropriate StorageEngine, It will iterate
over all of the available StorageEngines, calling
:meth:`engine.parse() <mediacore.lib.storage.StorageEngine.parse>`
with the file or string objects as parameters. If a given StorageEngine is
capable of handling the provided data, it will return a metadata dict as
described in the
:meth:`mediacore.lib.storage.StorageEngine.parse`
docstring.  If a StorageEngine is incapable of handling the provided data, it
will raise a
:class:`mediacore.lib.storage.UnsuitableEngineError`.

In order to ensure that the optimal StorageEngine is chosen, each StorageEngine
class is responsible for defining a list of which other StorageEngine classes
should come before it and which ones should come after it. For example, the
StorageEngine responsible for uploading to a remote FTP server should be
preferred over the default local file StorageEngine, while both should be
tested before any URL-based StorageEngines, to ensure that if the user has
somehow uploaded a file and provided a URL string, the uploaded file takes
precedence over the text input. Likewise, the YouTube StorageEngine should be
tested before the default RemoteURL storage engine so that a YouTube URL is not
misclassified as a playable file.

It is up to the programmers to ensure that there are no cycles in this
precedence graph. MediaDrop finds a topological ordering according to these
provided restrictions, and iterates in that order.

The main logic for handling the creation of new MediaFiles is in the function
:func:`mediacore.lib.storage.add_new_media_file`. It is worthwhile to become
familiar with its workings before attempting to write a new StorageEngine.


Implementation
--------------

A new StorageEngine can be added to MediaDrop simply by subclassing
:class:`mediacore.lib.storage.StorageEngine` and registering that subclass with
the Abstract Base Class.

Refer to the :file:`mediacore/lib/storage/__init__.py` file to see which
properties must be implemented (all properties initialized as
:class:`abstractproperty <mediacore.plugin.abc.abstractproperty>`
and all methods decorated by
:func:`abstractmethod <mediacore.plugin.abc.abstractmethod>`
must be implemented in subclasses).

.. sourcecode:: python

   from mediacore.lib.storage import StorageEngine

   class MyStorage(StorageEngine):
       """
       Implement all abstract properties and abstract methods here ...
       """

   StorageEngine.register(MyStorage)

As mentioned above, StorageEngines can optionally define a dict of editable
properties in their
:attr:`_default_data <mediacore.lib.storage.StorageEngine._default_data>`
dict if they also provide a subclass of
:class:`mediacore.forms.admin.storage.StorageForm` whose
:meth:`display <mediacore.forms.admin.storage.StorageForm.display>` and
:meth:`save_engine_params <mediacore.forms.admin.storage.StorageForm.save_engine_params>`
methods can map the form values to and from the data dict. StorageEngines that
do this will have links, in MediaDrop's admin backend, to a page where an admin
can use the rendered form to edit the StorageEngine's properties.  An example
of a StorageEngine that has this feature is
:class:`mediacore.lib.storage.localfiles.LocalFileStorage`.



Abstract Base Class
-------------------

.. automodule:: mediacore.lib.storage

.. autoclass:: StorageEngine
   :members:

   .. automethod:: __init__
   .. autoattribute:: _default_data


Related Functions
-----------------

.. autofunction:: add_new_media_file

Related Classes
---------------

.. autoclass:: mediacore.lib.uri.StorageURI
   :members:

   .. automethod:: __init__


.. autoclass:: mediacore.forms.admin.storage.StorageForm
   :members:

