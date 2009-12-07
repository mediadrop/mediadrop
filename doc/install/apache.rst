.. _install_apache:

============================
Apache & mod_wsgi Deployment
============================

Installation of Apache and mod_wsgi is beyond the scope of this
document. Please refer to the documentation for `Apache
<http://httpd.apache.org/>`_ and `mod_wsgi
<http://code.google.com/p/modwsgi/wiki/InstallationInstructions>`_ for
that.

Here is an example Apache configuration, assuming you want to deploy to
``yourdomain.com/base/``. If you'd like to deploy to the root directory,
that can be done as well, but to access static data outside of that
directory, you must create more exceptions with ``Alias``.

This can be put in your ``httpd.conf`` file:

.. sourcecode:: apacheconf

    # You can tweak this next line to your heart's content based on the mod_wsgi
    documentation
    # but this should work for now.
    WSGIDaemonProcess mcore threads=1 display-name=%{GROUP}
    WSGIProcessGroup mcore

    # We'll make the root directory of the domain call the wsgi script
    WSGIScriptAlias /base/ /home/someuser/mediacore/wsgi-scripts/wsgi-deployment.py

    # Make the wsgi script accessible
    <Directory /home/someuser/mediacore/wsgi-scripts>
        Order allow,deny
        Allow from all
    </Directory>

    # We'll need to create exceptions for all static content.
    Alias /base/styles /home/someuser/mediacore/mediacore/public/styles
    Alias /base/images /home/someuser/mediacore/mediacore/public/images
    Alias /base/scripts /home/someuser/mediacore/mediacore/public/scripts
    Alias /base/admin/styles /home/someuser/mediacore/mediacore/public/admin/styles
    Alias /base/admin/images /home/someuser/mediacore/mediacore/public/admin/images
    Alias /base/admin/scripts /home/someuser/mediacore/mediacore/public/admin/scripts

    # Make all the static directories accessible
    <Directory /home/someuser/mediacore/mediacore/public/\*>
        Order allow,deny
        Allow from all
    </Directory>


