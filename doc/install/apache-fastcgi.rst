.. _install_apache-fastcgi:

===============================
Apache & mod_fcgid Deployment
===============================

The Apache/mod_fcgid setup is intended as an easy way for users with shared
hosting environments to use python webapps. It adds some overhead over the
:ref:`install_apache-wsgi`, so if you administrate your own server, you may
want to use that instead.

This tutorial assumes that you already have Apache and mod_fcgid installed
and working (mod_fastcgi works as well). If you're unsure, check with your
hosting provider.

Components
----------
The following six components are involved in getting web requests through to
MediaCore CE with this setup. Don't worry if this sounds like a lot! By this
stage you already have three, and the remaining ones are very easy to set up.

``Apache``
   the web server

``mod_fcgid`` or (unmaintained) ``mod_fastcgi``
   Apache module that lets Apache run FastCGI scripts

``.htaccess``
   tells Apache which requests to send to our FastCGI script

``mediacore.fcgi``
   the FastCGI script, uses flup to run MediaCore CE

``flup``
   provides a WSGI interface for MediaCore CE to get data from Apache

``mediacore``
   the reason we're here!

Instructions
------------
**NOTE 1:** You should have already created a ``deployment.ini`` file and set
the permissions on the ``data`` subdirectories as outlined in
:ref:`production_deployments`

**NOTE 2:** The following instructions assume that you're deploying MediaCore CE
to ``http://yourdomain.com/my_media/``. To deploy MediaCore CE to any other
directory of your website, the process is very simple: Instead of putting the
files into ``/path/to/document_root/my_media``, like in the instructions below,
put them into whichever directory (inside your docroot) you want to serve from.

**NOTE 3:** If deploying MediaCore CE inside an existing directory, you must make
sure that the MediaCore CE .htaccess file doesn't overwrite any existing
.htaccess file in that directory--you'll have to copy the contents over to the
existing .htaccess file if there is one, and make sure that the contents of
the two files make sense together.

First, install the ``flup`` Python package:

.. sourcecode:: bash

   # If your virtual environment is not activated, activate it:
   source /path/to/mediacore_env/bin/activate

   # Install flup:
   easy_install flup

Second, create a directory named ``my_media`` inside your website's document
root. Copy all the files from ``/path/to/mediacore_install/deployment-scripts/mod_fastcgi``
into the new ``my_media`` directory (this includes ``.htaccess``,
``mediacore.fcgi``, and ``mediacore-restart.sh``).

.. sourcecode:: bash

   # Create the my_media directory:
   cd /path/to/document_root
   mkdir my_media

   # Copy the deployment files
   cp /path/to/mediacore_install/deployment-scripts/mod_fastcgi/* ./my_media/
   cp /path/to/mediacore_install/deployment-scripts/mod_fastcgi/.htaccess ./my_media/

Third, create symbolic links (symlinks) to the ``public`` and the ``data``
directory from your MediaCore CE installation:

.. sourcecode:: bash

   # Create a symlink to the public directory
   ln -sf /path/to/mediacore_install/mediacore/public ./my_media/public

   # Create a symlink to the data directory
   ln -sf /path/to/mediacore_install/data ./my_media/data

Fourth, you'll need to edit the paths in ``my_media/mediacore.fcgi`` to point
to your own MediaCore CE installation and virtual environment. The **four (4)**
lines you need to edit are at the top of the file, and look like this:

.. sourcecode:: python

   #!/path/to/mediacore_env/bin/python
   python_egg_cache = '/path/to/mediacore_install/data/python-egg-cache'
   deployment_config = '/path/to/mediacore_install/deployment.ini'
   temp_dir = '/path/to/mediacore_install/data/tmp'

Finally, you need to configure mod_fcgid for large uploads (this step is not
necessary for mod_fastcgi). Please add this line to your Apache configuration
(the ``.htaccess`` file is not enough for this to work!)

.. sourcecode:: bash

    # set the max upload size to 300 MB (number is the size in bytes)
    FcgidMaxRequestLen 314572800


Testing Installation
--------------------
Our first step after deployment is to test the app. To get FastCGI to run
MediaCore CE for the first time, point your browser to ``http://yourdomain/my_media``

If you don't see MediaCore CE make sure you've followed all of the instructions above!

Performance Enhancements
------------------------
By default, all files are served through MediaCore CE. The configuration above
ensures that Apache will serve all static files (.css, .js, and images)
directly, but MediaCore CE will still check for static files before serving any
page. There are two speedups we can enable here.

First, edit one line in ``/path/to/mediacore_install/deployment.ini``. Find
the static_files line, and set it to false.

.. sourcecode:: ini

   static_files = false

The second speedup is only available if you have mod_xsendfile installed and
enabled in Apache. MediaCore CE can take advantage of mod_xsendfile and have
Apache serve all media files (.mp3, .mp4, etc.) directly. To enable this, edit
another line in ``/path/to/mediacore_install/deployment.ini``. Find the
files_serve_method line, and set it to apache_xsendfile.

.. sourcecode:: ini

   files_serve_method = apache_xsendfile

Editing MediaCore CE
--------------------
If you make any changes to your MediaCore CE installation while Apache is running
(eg. if you upgrade MediaCore CE or make any customizations), you'll need to make
sure that mod_fastcgi recognizes those changes.

The easiest way to do this is to 'touch' the .fcgi script. This will modify the
'last modified on' timestamp of the file, so that mod_fastcgi thinks it has been
updated and will read and re-load it.

.. sourcecode:: bash

   # Navigate to the my_media directory:
   cd /path/to/document_root
   cd my_media

   # Force a refresh of the MediaCore CE code
   touch mediacore.fcgi
