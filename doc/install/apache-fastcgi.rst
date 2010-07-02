.. _install_apache-fastcgi:

===============================
Apache & mod_fastcgi Deployment
===============================

The Apache/mod_fastcgi setup is intended as an easy way for users with shared
hosting environments to use python webapps. It adds some overhead over the
:ref:`install_apache-wsgi`, so if you administrate your own server, you may
want to use that instead.

This tutorial assumes that you already have Apache and mod_fastcgi installed
and working. If you're unsure, check with your hosting provider.

Components
----------
The following six components are involved in getting web requests through to
mediacore with this setup. Don't worry if this sounds like a lot! By this
stage you already have three, and the remaining ones are very easy to set up.

``Apache``
   the web server

``mod_fastcgi``
   Apache module that lets Apache run FastCGI scripts

``.htaccess``
   tells Apache which requests to send to our FastCGI script

``mediacore.fcgi``
   the FastCGI script, uses flup to run mediacore

``flup``
   provides a WSGI interface for mediacore to get data from Apache

``mediacore``
   the reason we're here!

Instructions
------------
**NOTE 1:** The following instructions assume that you're deploying MediaCore
to ``http://yourdomain.com/my_media/``. To deploy mediacore to any other
directory of your website, the process is very simple: Instead of putting the
files into ``/path/to/document_root/my_media``, like in the instructions below,
put them into the folder you want to serve from, and change the prefix config
line to match.

**NOTE 2:** If deploying mediacore inide an existing directory, you must make
sure that the mediacore .htaccess file doesn't overwrite any existing
.htaccess file in that directory--you'll have to copy the contents over to the
existing .htaccess file if there is one, and make sure that the contents of
the two files make sense together.

First, install the ``flup`` Python package:

.. sourcecode:: bash

   # If your virtual environment is not activated, activate it:
   source /path/to/mediacore_env/bin/activate

   # Install flup:
   easy_install flup

Second, create a temporary directory and a python cache directory for your
deployment to use.

.. sourcecode:: bash

   cd /path/to/mediacore_install/data
   mkdir tmp
   mkdir python-egg-cache

**Permissions:**
Now is a good time to make sure that all of the apropriate files have the
correct permissions. The following files/directories should be writeable by
your apache user.
(Depending on how your server is set up, the user name may be different).

1. all of the folders inside the ``/path/to/mediacore_install/data/``
#. ``/path/to/mediacore_install/mediacore/public/images/podcasts/``
#. ``/path/to/mediacore_install/mediacore/public/images/media/``

Third, create a directory named ``my_media`` inside your website's document
root. Copy all the files from ``/path/to/mediacore_install/deployment-scripts/mod_fastcgi``
into the new ``my_media`` directory (this includes ``.htaccess``,
``mediacore.fcgi``, and ``mediacore-restart.sh``).

.. sourcecode:: bash

   # Create the my_media directory:
   cd /path/to/document_root
   mkdir my_media

   # Copy the deployment files
   cp /path/to/mediacore/install/deployment-scripts/mod_fastcgi/* ./my_media/
   cp /path/to/mediacore/install/deployment-scripts/mod_fastcgi/.htaccess ./my_media/

**Permissions:**
Make sure that the ``./my_media/fastcgi.pid`` file is writeable by your apache user.

Fourth, create a symbolic link (symlink) to the ``public`` directory from your
mediacore installation:

.. sourcecode:: bash

   # Create a symlink to the public directory
   ln -sf /path/to/mediacore/install/mediacore/public ./my_media/public

Fifth, you'll need to edit the paths in ``my_media/mediacore.fcgi`` to point
to your own mediacore installation and virtual environment. The **four (4)**
lines you need to edit are at the top of the file, and look like this:

.. sourcecode:: python

   #!/path/to/mediacore_env/bin/python
   python_egg_cache = '/path/to/mediacore_install/data/python-egg-cache'
   deployment_config = '/path/to/mediacore_install/deployment.ini'
   temp_dir = '/path/to/mediacore_install/data/tmp'

Finally, edit one line in ``/path/to/mediacore_install/deployment.ini``. Find
the proxy_prefix line, uncomment it, and set the prefix to ``/my_media``. This
will ensure that the URLs generated within the application point to the right
place:

.. sourcecode:: ini

   proxy_prefix = /my_media

Testing Installation
--------------------
Our first step after deployment is to test the app. To get FastCGI to run
MediaCore for the first time, point your browser to ``http://yourdomain/my_media``

If you don't see MediaCore make sure you've followed all of the instructions above!

Performance Enhancements
------------------------
By default, all files are served through MediaCore. The configuration above
ensures that Apache will serve all static files (.css, .js, and images)
directly, but MediaCore will still check for static files before serving any
page. There are two speedups we can enable here.

First, edit one line in ``/path/to/mediacore_install/deployment.ini``. Find
the static_files line, and set it to false.

.. sourcecode:: ini

   static_files = false

The second speedup is only available if you have mod_xsendfile installed and
enabled in Apache. MediaCore can take advantage of mod_xsendfile and have
Apache serve all media files (.mp3, .mp4, etc.) directly. To enable this, edit
another line in ``/path/to/mediacore_install/deployment.ini``. Find the
files_serve_method line, and set it to apache_xsendfile.

.. sourcecode:: ini

   files_serve_method = apache_xsendfile

Editing MediaCore
-----------------
If you make any changes to your MediaCore installation while Apache is running
you'll need to make sure that mod_fastcgi recognizes those changes.

The easiest way to do this is to stop the process that's running the app. A
script that does this is now included in the ``my_media`` folder you created
above:

.. sourcecode:: bash

   # Navigate to the my_media directory:
   cd /path/to/document_root
   cd my_media

   # Force a refresh of the mediacore code
   ./mediacore-restart.sh

   # This should have printed "MediaCore successfully stopped"
   # If so, we're done!
   # Visit http://yourdomain.com/my_media/ to see it in action!

If this results in in error message like this:

.. sourcecode:: text

   -bash: kill: (xxxxx) - No such process

Then MediaCore wasn't running properly in the first place.

If, however, it results in in error message like this:

.. sourcecode:: text

   -bash: kill: (xxxxx) - Operation not permitted

Then your Apache is not configured to run scripts as individualized users.
This means that MediaCore is running as a user that is not you!

* **If you have root access**, this isn't a problem; just use ``sudo`` to run
  the script.
* **If you don't have root access**, you'll need to run the script
  through Apache. You can do this by renaming it ``mediacore-restart.fcgi`` and
  visiting ``http://yourdomain.com/my_media/mediacore-restart.fcgi``.

