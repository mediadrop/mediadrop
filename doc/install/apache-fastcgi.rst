.. _install_apache-fastcgi:

============================
Apache & mod_fastcgi Deployment
============================

Installation of Apache and mod_fastcgi is beyond the scope of this
document. In fact, if you have the capability to install mod_fastcgi,
you should probably look at setting up mod_wsgi instead--it'll reduce
overhead.

Here is an example Apache .htaccess, assuming you want to deploy to
``yourdomain.com/my_media/``. If you'd like to deploy to the root directory,
that can be done as well, but to access static data outside of that
directory, you must create more exceptions with ``RewriteRule`` s.

Create a directory named ``my_media`` in your webservers document root.
Copy the config below into a file named ``.htaccess`` inside that directory.

.. sourcecode:: apacheconf

    # .htaccess

    Options +ExecCGI
    AddHandler fastcgi-script .fcgi
    RewriteEngine On

    # Create rewrite rules for pointing mediacore requests to fastcgi script
    RewriteRule ^mediacore\.fcgi(/.*)$  - [L]
    RewriteRule ^(.*)$  mediacore.fcgi/$1 [L]

    # Create rewrite rules for serving static content
    RewriteRule ^public(/?.*)$ - [L]
    RewriteRule ^(admin/)?(styles|images|scripts)/(.*)$ public/$1$2/$3 [L]

Next, create symbolic links (symlinks) to the ``mediacore.fcgi`` script and
the ``public`` directory from your mediacore installation:

.. sourcecode::

    cd /path/to/document_root/my_media
    cp /path/to/mediacore/install/deployment-scripts/fastcgi.htaccess .htaccess
    ln -sf /path/to/mediacore/install/deployment-scripts/mediacore.fcgi mediacore.fcgi
    ln -sf /path/to/mediacore/install/mediacore/public public

Here is an example for your ``mediacore.fcgi`` script (included in the
``deployment-scripts`` dir in your mediacore installation):

.. sourcecode:: python

    # mediacore.fcgi

    #!/Users/anthony/python_environments/mediacore_env/bin/python
    import sys, os
    os.environ['PYTHON_EGG_CACHE'] = '/path/to/mediacore_install/python-wsgi-egg-cache'

    from paste.deploy import loadapp
    application = loadapp('config:/path/to/mediacore_install/deployment.ini')

    if __name__ == '__main__':
        from flup.server.fcgi import WSGIServer
        WSGIServer(app).run()

