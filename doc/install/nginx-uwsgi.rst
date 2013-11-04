:orphan:

.. _install_nginx-uwsgi:

========================
NGINX & uWSGI Deployment
========================

**NOTE 1:** This tutorial assumes that you already have NGINX and uWSGI installed.
If you're on a shared hosting platform, and don't have the ability to install
uWSGI and NGINX, have no fear. Your hosting provider probably already supports
mod_fastcgi so check out the :ref:`install_apache-fastcgi` tutorial.

**NOTE 2:** If you're administrating your own system and looking for pointers on how
to get uWSGI or NGINX installed, check out the developer's site.

`uWSGI main site
<http://projects.unbit.it/uwsgi/>`_.
You can find example configurations as
well as the official documentation on uWSGI here.

`uWSGI Mailing List
<http://lists.unbit.it/cgi-bin/mailman/listinfo/uwsgi>`_.
uWSGI also has a fantastic mailing list where the author contributes daily, and
is always willing to help out new users try to work through their issues.

`NGINX main site
<http://wiki.nginx.org>`_.
This is the main NGINX Wiki that where you can
find the full documentation for NGINX, all NGINX modules as well as many
recipes and tips for configuring NGINX.

Components
----------
The following five components are involved in getting web requests through to
MediaDrop with this setup.

``NGINX``
   the web server

``uWSGI``
   WSGI application container that serves MediaDrop

``nginx.conf``
   Your nginx configuration file.

``deployment.ini``
   The MediaDrop deployment file for your production server.

``mediadrop``
   the reason we're here!

Instructions
------------
**NOTE 1:** You should have already created a ``deployment.ini`` file and set
the permissions on the ``data`` subdirectories as outlined in
:ref:`production_deployments`

**NOTE 2:** The following instructions assume that you’re deploying MediaDrop
to your own domain at ``http://site.example`` and that your MediaDrop
installation is configured like this:

``MediaDrop Virtual Environment > /path/to/venv``
``MediaDrop Source Code > /path/to/mediadrop_install``

uWSGI Configuration
-------------------

The first thing you will want to do is to add a new [uwsgi] section to your
deployment.ini file. This section will contain various parameters for the uWSGI
server and will automatically load your application when NGINX passes requests
over to it. Here is a good base for your uWSGI parameters, and explained in
more detail below:

.. sourcecode:: ini

    [uwsgi]
    socket = /tmp/uwsgi-mediadrop.soc
    master = true
    processes = 5
    home = /path/to/venv
    daemonize = /var/log/uwsgi.log

``socket:`` uWSGI will create a unix socket at this location on your system
that will listen for incoming requests. You can also use a TCP socket, but if
you are running NGINX on the same server as uWSGI, a standard unix socket will
be much faster. This socket name will be used again in your NGINX configuration
to pass requests into uWSGI.

``master:`` Enables uWSGI master process manager. You should be enabling this
unless you have a good reason not to.

``processes:`` The number of uWSGI worker processes to spawn.

``home:`` This defines your apps home / VirtualEnvironment and will allow uWSGI
to correctly find your app. If you get errors about your app not loading,
check that this setting is correct first.

``daemonize:`` Run uWSGI in daemon mode, and log all data to the file specified.

Now that you have created a [uwsgi] ini block in deployment.ini, you can launch
uWSGI and point to your ini file like this:

.. sourcecode:: bash

    # launch uWSGI and serve with settings from your config file
    sudo uwsgi --ini-paste /path/to/deployment.ini

If everything went well uWSGI will now be listening on the unix socket you
specified above. Of course you still need to tell NGINX how to talk to uWSGI so
let's configure that now.

NGINX Configuration
-------------------

When configuring NGINX for use with uWSGI to serve MediaDrop, you need to make
sure that you define how to talk to uWSGI, your static file paths, and also
your XSendfile internal path that MediaDrop will serve media files from.

At this point, it will probably be easier to just walk through a fully
functional MediaDrop NGINX configuration file, so here it is. This is a generic
configuration and will probably suit most use cases:

.. sourcecode:: nginx

    # Configure our MediaDrop App for NGINX+UWSGI
    server {
        # Define server parameters:
        # Listen on port 80 for requests to mydomain.com
        # log to /path/to/nginx/logs/mydomain.access.log using the main log format.
        listen       80;
        server_name  mydomain.com;
        access_log  logs/mydomain.access.log  main;

        # Important: This setting will define maximum upload size, so make
        # sure it is sane for your purposes! For example, if you have a
        # 300MB upload limit in MediaDrop, people will say "Yay! I can upload
        # my 300MB video!" However, if this setting is set to 10MB, then no
        # one will be able to upload videos over 10MB and people will not
        # like you very much.
        client_max_body_size 1500M;

        # Define NGINX Static File Paths
        #
        # First, define our default document root for static file serving.
        # NGINX configuration uses inheritance, so defining our base root here
        # will assign it to every other location{} declaration unless an
        # alternate path is specified. Also, any files that reside in the root will
        # of course not need to be defined as they are included. An example
        # would be /crossdomain.xml
        #
        # * Note: The ~* used in our location block regexes activates
        # case insensitive matching on the paths. This may or may not be
        # what you are after in your configuration. If you want /path and /Path
        # to be different paths, then just use ~ not ~*
        #
        # See the NGINX docs on Location  regex matching for more details:
        # http://wiki.nginx.org/HttpCoreModule#location

        root /path/to/mediadrop_install/mediadrop/public;

        # And now we define the rest of our static locations below
        location ~* ^/(appearance)/ {
                root /path/to/data ;
                break;
        }

        # All media and podcast images
        location ~* ^(/images\/media|images\/podcasts) {
                root /path/to/data ;
                break;
        }

        # Our standard public file paths
        location ~* ^/(styles|scripts|images)/ {
                expires max;
                add_header Cache-Control "public";
                break;
        }

        # Configure NGINX XSendfile.
        # We use an alias here instead of root so the path info
        # __mediadrop_serve__ is stripped off.
        # Note: "__mediadrop_serve__" is just the default prefix and can be
        # configured using the option "nginx_serve_path" in your deployment.ini.
        # Note: __mediadrop_serve__ should point to the path where MediaDrop
        # stores its media files.
        # Note: We define this as an "internal" location to prevent it from
        # being served directly to end users.
        location /__mediacore_serve__ {
                alias /path/to/data/media;
                internal;
        }

        # Declare our default location to pass through to our app
        # This will match any request not defined above and pass it to uWSGI
        # Note: The uwsgi_pass directive must use the same socket that was
        # defined in your deployment.ini [uwsgi] block.
        # Note: Make sure that you pass in SCRIPT_NAME = '' otherwise uWSGI
        # will raise a keyError when loading MediaDrop.
        location / {
                uwsgi_pass      unix:///tmp/uwsgi-mediadrop.soc;
                include         uwsgi_params;
                uwsgi_param     SCRIPT_NAME '';
        }
    }

At this point you can start your NGINX server and test out your app!


Performance Enhancements
------------------------
By default, all files are served through MediaDrop. The configuration above
ensures that NGINX will serve all static files (.css, .js, and images) directly,
but MediaDrop will still check for static files before serving any page. There
are two speedups we can enable here.

First, edit one line in ``/path/to/deployment.ini``.
Find the static_files line, and set it to false.

.. sourcecode:: ini

    # disable static file serving with MediaDrop
    static_files = false

The second speedup will allow MediaDrop to take advantage of NGINX XSendfile
and have NGINX serve all media files (.mp3, .mp4, etc.) directly. To enable
this, edit another line in ``/path/to/deployment.ini``.
Find the files_serve_method line, and set it to nginx_redirect.

.. sourcecode:: ini

    # enable NGINX as te default file serve method
    files_serve_method = nginx_redirect

