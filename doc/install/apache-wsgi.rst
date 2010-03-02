.. _install_apache-wsgi:

============================
Apache & mod_wsgi Deployment
============================

Installation of Apache and mod_wsgi is beyond the scope of this
document. Please refer to the documentation for `Apache
<http://httpd.apache.org/>`_ and `mod_wsgi
<http://code.google.com/p/modwsgi/wiki/InstallationInstructions>`_ for
that.

More detailed instructions can be found in this `blog post
<http://getmediacore.com/blog/turbogears-2-tg2-with-mod_wsgi-and-virtual-environments/>`_,

Here is an example Apache configuration, assuming you want to deploy to
``yourdomain.com/my_media/``. If you'd like to deploy to the root directory,
that can be done as well, but to access static data outside of that
directory, you must create more exceptions with ``Alias``.

This can be put in your ``httpd.conf`` file:

.. sourcecode:: apacheconf

    # You can tweak this next line to your heart's content based on the mod_wsgi documentation
    # but this should work for now.
    WSGIDaemonProcess mcore threads=1 display-name=%{GROUP}
    WSGIProcessGroup mcore

    # Intercept all requests to /my_media/* and pass them to mediacore.wsgi
    WSGIScriptAlias /my_media/ /path/to/mediacore_install/deployment-scripts/mediacore.wsgi

    # Make the wsgi script accessible
    <Directory /path/to/mediacore_install/wsgi-scripts>
        Order allow,deny
        Allow from all
    </Directory>

    # Create exceptions for all static content
    Alias /my_media/styles /path/to/mediacore_install/mediacore/public/styles
    Alias /my_media/images /path/to/mediacore_install/mediacore/public/images
    Alias /my_media/scripts /path/to/mediacore_install/mediacore/public/scripts
    Alias /my_media/admin/styles /path/to/mediacore_install/mediacore/public/admin/styles
    Alias /my_media/admin/images /path/to/mediacore_install/mediacore/public/admin/images
    Alias /my_media/admin/scripts /path/to/mediacore_install/mediacore/public/admin/scripts

    # Make all the static content accessible
    <Directory /path/to/mediacore_install/mediacore/public/*>
        Order allow,deny
        Allow from all
    </Directory>

Here is an example for your ``mediacore.wsgi`` script:

.. sourcecode:: python

    # mediacore.wsgi

    import os, sys, site

    # Make this folder writable by apache
    os.environ['PYTHON_EGG_CACHE'] = '/path/to/mediacore_install/python-wsgi-egg-cache'

    sd = '/path/to/mediacore_env/lib/python2.5/site-packages/'
    site.addsitedir(sd)

    from mediacore import debug
    from paste.deploy import loadapp

    application = loadapp('config:/path/to/mediacore_install/deployment.ini')

