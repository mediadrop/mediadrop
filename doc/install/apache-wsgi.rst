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
mediacore with this setup. Don't worry if this sounds like a lot! By this
stage you already have three, and the remaining ones are very easy to set up.

``Apache``
   the web server

``mod_wsgi``
   Apache module that lets Apache host WSGI enabled Python applications

``httpd.conf``
   Your apache configuration; tells mod_wsgi how to run your app

``mediacore.wsgi``
   The script that runs mediacore as a WSGI application

``mediacore``
   the reason we're here!

Instructions
------------
**NOTE:** The following instructions assume that you're deploying MediaCore to
``http://yourdomain.com/my_media/``. To deploy mediacore to the root directory
of your website, see the instructions at the bottom of the page.

We will not actually be creating a ``my_media`` directory, but we will use
aliases in the Apache config to make sure that requests to
``http://yourdomain.com/my_media/`` are passed to MediaCore.

First, TODO: BLAH BLAH BLAH CREATE TEMP FOLDER AND PYTHON-EGG CACHE

Second, you'll need to edit the paths in ``/path/to/mediacore/install/deployment-scripts/mod_wsgi/mediacore.wsgi``
to point to your own mediacore installation and virtual environment. The
**two (2)** lines you need to edit are at the top of the file, and look like
this:

.. sourcecode:: python

   deployment_config = '/path/to/mediacore_install/deployment.ini'
   temp_dir = '/path/to/mediacore_install/data/tmp'

Finally, you will need to add the following lines to your Apache configuration.
Depending on your setup, you may want to add it to the main ``httpd.conf`` file,
or inside a VirtualHost include.

Make sure that you replace all references to ``/path/to/mediacore_install/``
and ``/path/to/mediacore_env`` with the correct paths for your own MediaCore
installation and virtual environment.

.. sourcecode:: apacheconf

    # You can tweak the WSGIDaemonProcess directive for performance, but this
    # will work for now.
    # Relevant doc pages:
    #     http://code.google.com/p/modwsgi/wiki/ProcessesAndThreading
    #     http://code.google.com/p/modwsgi/wiki/ConfigurationDirectives#WSGIDaemonProcess
    # Hint: pay attention to issues surrounding worker-mpm and prefork-mpm.

    WSGIDaemonProcess mcore \
        threads=1 \
        display-name=%{GROUP} \
        python-path=/path/to/mediacore_env/lib/python2.5/site-packages \
        python-eggs=/path/to/mediacore_install/python-egg-cache

    WSGIProcessGroup mcore

    # Intercept all requests to /my_media/* and pass them to mediacore.wsgi
    WSGIScriptAlias /my_media/ /path/to/mediacore_install/deployment-scripts/mod_wsgi/mediacore.wsgi

    # Make the wsgi script accessible
    <Directory /path/to/mediacore_install/wsgi-scripts>
        Order allow,deny
        Allow from all
    </Directory>

    # Create exceptions for all static content
    AliasMatch /my_media(/admin)/(images|scripts|styles)(/?.*) /path/to/mediacore_install/mediacore/public$1/$2$3

    # Make all the static content accessible
    <Directory /path/to/mediacore_install/mediacore/public/*>
        Order allow,deny
        Allow from all
    </Directory>

