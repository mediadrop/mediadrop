.. _install_apache-fastcgi:

===============================
Apache & mod_fastcgi Deployment
===============================

This tutorial assumes that you already have Apache and mod_fastcgi installed
and working.
TODO: Link to instructions to do this.

The Apache/mod_fastcgi setup is intended as an easy way for users with shared
hosting environments to use python webapps. It adds some overhead over the
Apache/mod_wsgi, so if you administrate your own server, you may want
to use that instead.

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
**NOTE:** The following instructions assume that you're deploying MediaCore to
``http://yourdomain.com/my_media/``. To deploy mediacore to the root directory
of your website, see the instructions at the bottom of the page.


First, install the ``flup`` Python package:

.. sourcecode:: bash

   # If your virtual environment is not activated, activate it:
   source /path/to/mediacore_env/bin/activate

   # Install flup:
   easy_install flup

Second, TODO: BLAH BLAH BLAH CREATE TEMP FOLDER AND PYTHON-EGG CACHE

Third, create a directory named ``my_media`` inside your website's document
root. Copy all the files from ``/path/to/mediacore_install/deployment-scripts/mod_fastcgi``
into the new ``my_media`` directory (this includes ``.htaccess``,
``mediacore.fcgi``, and ``mediacore-restart.sh``).

Fourth, create a symbolic link (symlink) to the ``public`` directory from your
mediacore installation:

To do steps 3 and 4 from a bash terminal:

.. sourcecode:: bash

   # Create the my_media directory:
   cd /path/to/document_root
   mkdir my_media

   # Copy the deployment files
   cp /path/to/mediacore/install/deployment-scripts/mod_fastcgi/* ./my_media/

   # Create a symlink to the public directory
   ln -sf /path/to/mediacore/install/mediacore/public ./my_media/public

Finally, you'll need to edit the paths in ``my_media/mediacore.fcgi`` to point
to your own mediacore installation and virtual environment. The **three (3)**
lines you need to edit are at the top of the file, and look like this:

.. sourcecode:: python

   #!/path/to/mediacore_env/bin/python
   python_egg_cache = '/path/to/mediacore_install/python-wsgi-egg-cache'
   deployment_config = '/path/to/mediacore_install/deployment.ini'

Testing Installation
--------------------
Our first step after deployment is to test the app. To get FastCGI to run
MediaCore for the first time, point your browser to ``http://yourdomain/my_media``

If you don't see MediaCore make sure you've followed all of the instructions above!

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

Installing to Your Site's Root Directory
----------------------------------------
If you'd rather host MediaCore from ``http://yourdomain.com/``, or from any
other already existing directory of your site, instead of from
``http://yourdomain.com/my_media/``, the process is very simple:
Instead of putting the files above into ``/path/to/document_root/my_media``
put them into the folder you want to serve from.

**NOTE:** However, you must make sure that the mediacore .htaccess file
doesn't overwrite any existing .htaccess file in that directory--you'll have
to copy the contents over to the existing .htaccess file if there is one, and
make sure that the contents of the two files make sense together.

