:orphan:

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
MediaDrop with this setup. Don't worry if this sounds like a lot! By this
stage you already have three, and the remaining ones are very easy to set up.

``Apache``
   the web server

``mod_fcgid`` or (unmaintained) ``mod_fastcgi``
   Apache module that lets Apache run FastCGI scripts

``.htaccess``
   tells Apache which requests to send to our FastCGI script

``mediadrop.fcgi``
   the FastCGI script, uses flup to run MediaDrop

``flup``
   provides a WSGI interface for MediaDrop to get data from Apache

``mediadrop``
   the reason we're here!

Instructions
------------
**NOTE 1:** You should have already created a ``deployment.ini`` file and set
the permissions on the ``data`` subdirectories as outlined in
:ref:`production_deployments`

**NOTE 2:** The following instructions assume that you're deploying MediaDrop
to ``http://site.example/my_media/``. To deploy MediaDrop to any other
directory of your website, the process is very simple: Instead of putting the
files into ``/path/to/document_root/my_media``, like in the instructions below,
put them into whichever directory (inside your docroot) you want to serve from.

**NOTE 3:** If deploying MediaDrop inside an existing directory, you must make
sure that the MediaDrop .htaccess file doesn't overwrite any existing
.htaccess file in that directory – you'll have to copy the contents over to the
existing .htaccess file if there is one, and make sure that the contents of
the two files make sense together.

First, install the ``flup`` Python package:

.. sourcecode:: bash

   # If your virtual environment is not activated, activate it:
   source /path/to/venv/bin/activate

   # Install flup:
   easy_install flup

Second, create a directory named ``my_media`` inside your website's document
root. Copy ``.htaccess`` and ``mediadrop.fcgi`` from 
``/path/to/mediadrop_install/deployment-scripts/mod_fastcgi`` into the new 
``my_media`` directory.

.. sourcecode:: bash

   # Create the my_media directory:
   cd /path/to/document_root
   mkdir my_media

   # Copy the deployment files
   cp /path/to/mediadrop_install/deployment-scripts/mod_fastcgi/mediadrop.fcgi ./my_media/
   cp /path/to/mediadrop_install/deployment-scripts/mod_fastcgi/.htaccess ./my_media/

Third, create symbolic links (symlinks) to the ``public`` and the ``data``
directory from your MediaDrop installation:

.. sourcecode:: bash

   # Create a symlink to the public directory
   ln -sf /path/to/mediadrop_install/mediadrop/public ./my_media/public

   # Create a symlink to the data directory
   ln -sf /path/to/data ./my_media/data

Fourth, you'll need to edit the paths in ``my_media/mediadrop.fcgi`` to point
to your own MediaDrop installation and virtual environment. The **four (4)**
lines you need to edit are at the top of the file, and look like this:

.. sourcecode:: python

    #!/path/to/venv/bin/python
    python_egg_cache = '/path/to/data/python-egg-cache'
    deployment_config = '/path/to/deployment.ini'
    temp_dir = '/path/to/data/tmp'

Finally, you need to configure mod_fcgid for large uploads (this step is not
necessary for mod_fastcgi). Please add this line to your Apache configuration
(the ``.htaccess`` file is not enough for this to work!)

.. sourcecode:: bash

    # set the max upload size to 300 MB (number is the size in bytes)
    FcgidMaxRequestLen 314572800


Testing the Installation
------------------------

If you don't see MediaDrop running on ``http://site.example/my_media`` you 
can run ``./my_media/mediadrop.fcgi`` on the command line. If you see a lot 
of HTML output, the installation itself is good but there is a problem with your
Apache configuration or permission setup. A Python traceback means that 
MediaDrop itself is not correctly installed but the problem should be easy
to diagnose (don't forget to check the forum).

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
sure that mod_fcgid recognizes those changes.

For that you need to ``kill`` the appropriate mod_fcgid processes (or just 
restart Apache).

