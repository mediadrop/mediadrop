:orphan:

.. _install_apache-wsgi:

============================
Apache & mod_wsgi Deployment
============================

**NOTE 1:** This tutorial assumes that you already have Apache and mod_wsgi installed.
If you're on a shared hosting platform, and don't have the ability to install
mod_wsgi, have no fear. Your hosting provider probably already supports
mod_fastcgi so check out the :ref:`install_apache-fastcgi` tutorial.

**NOTE 2:** If you're administrating your own system and looking for pointers on how
to get mod_wsgi installed, check out the developer's site; the documentation is
verbose, but very complete: `mod_wsgi main site
<http://code.google.com/p/modwsgi/wiki/InstallationInstructions>`_.

Components
----------
The following five components are involved in getting web requests through to
MediaDrop with this setup. Don't worry if this sounds like a lot! By this
stage you already have three, and the remaining ones are very easy to set up.

``Apache``
   the web server

``mod_wsgi``
   Apache module that lets Apache host WSGI enabled Python applications

``httpd.conf``
   Your apache configuration; tells mod_wsgi how to run your app

``mediacore.wsgi``
   The script that runs MediaDrop as a WSGI application

``mediacore``
   The reason we're here!

Instructions
------------
**NOTE 1:** You should have already created a ``deployment.ini`` file and set
the permissions on the ``data`` subdirectories as outlined in
:ref:`production_deployments`

**NOTE 2:** The following instructions assume that you're deploying MediaDrop
to ``http://site.example/my_media/``. To deploy MediaDrop to any other path,
simply replace all references to ``/my_media`` below with your desired path.
If MediaDrop should run at the URL root (no subdirectory), just remove the
references to ``/my_media`` entirely.

**NOTE 3:** We will not actually be creating a ``my_media`` directory, but we
will use aliases in the Apache config to make sure that requests to
``http://site.example/my_media/`` are passed to MediaDrop.

First, copy the ``mediacore.wsgi`` file from ``/path/to/mediadrop_install/deployment-scripts/mod_wsgi/mediacore.wsgi``
to the directory where your ``deployment.ini`` is. Then edit the paths in the
wsgi file to point to your own MediaDrop installation and virtual environment. The
**two** lines you need to edit are at the top of the file, and look like
this:

.. sourcecode:: python

   deployment_config = '/path/to/deployment.ini'
   temp_dir = '/path/to/data/tmp'

Finally, you will need to add the following lines to your Apache configuration.
Depending on your setup, you may want to add it to the main ``httpd.conf`` file,
or inside a VirtualHost include.

Make sure that you replace all references to ``/path/to/mediadrop_install/``
and ``/path/to/venv/`` with the correct paths for your own MediaDrop
source code and virtual environment.

.. literalinclude:: ../../deployment-scripts/mod_wsgi/apache-config.sample


Performance Enhancements
------------------------
By default, all files are served through MediaDrop. The configuration above
ensures that Apache will serve all static files (.css, .js, and images)
directly, but MediaDrop will still check for static files before serving any
page. There are two speedups we can enable here.

First, edit one line in ``/path/to/deployment.ini``. Find
the static_files line, and set it to false.

.. sourcecode:: ini

   static_files = false

The second speedup is only available if you have mod_xsendfile installed and
enabled in Apache. MediaDrop can take advantage of mod_xsendfile and have
Apache serve all media files (.mp3, .mp4, etc.) directly. To enable this, edit
another line in ``/path/to/deployment.ini``. Find the
files_serve_method line, and set it to apache_xsendfile.

.. sourcecode:: ini

   files_serve_method = apache_xsendfile


Changing the MediaDrop Source Code
-------------------------------------
If you make any changes to your MediaDrop installation while Apache is running
(eg. if you upgrade MediaDrop or make any customizations), you'll need to make
sure that mod_wsgi recognizes those changes.

The easiest way to do this is to 'touch' the .wsgi script. This will modify the
'last modified on' timestamp of the file, so that mod_wsgi thinks it has been
updated and will read and re-load it.

.. sourcecode:: bash

   # Navigate to the directory where your modified mediacore.wsgi is
   cd /path/to/...
   
   # Force a refresh of the MediaDrop code
   touch mediacore.wsgi

