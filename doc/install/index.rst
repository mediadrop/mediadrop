.. _install_toplevel:

============
Installation
============

Getting started with Python web apps can sometimes be a little
overwhelming, but we've tried to streamline the process as much as
possible.


Quick Overview
--------------

For those already familiar with installing Pylons/TurboGears apps, the
process will be very familiar:

1. Create and activate a new ``virtualenv``.
2. Run ``python setup.py develop`` to install MediaCore and its
   dependencies.
3. For production, run ``paster make-config mediacore deployment.ini``
   and to create a unique ``deployment.ini`` config. On development
   machines there's already a ``development.ini`` file for you to use.
4. Configure your database credentials in the ini config file.
5. Import ``setup.sql`` using ``mysqlimport``, phpMyAdmin or any other
   tool.
6. Run ``paster serve path/to/your/config.ini`` and test it out!


Requirements
------------

MediaCore must be run on a \*nix operating system. We've got it running
on CentOS and Mac OS X without issue. Windows is unsupported at this
time.

This guide assumes that you already have installed:

* Python 2.5.x or newer
* MySQL 5.0.x or newer
* GCC must be installed on your ``$PATH`` for certain dependencies to
  compile automatically. For Mac OS X users, that means installing
  `Xcode <http://developer.apple.com/tools/xcode/>`_.

By the time you're done installing you will also have:

* The python ``virtualenv`` package
* The python ``MySQLdb`` database adapter
* To run on Apache, either
  * the Apache ``mod_wsgi`` module, or
  * the python ``flup`` package and the Apache  ``mod_fastcgi`` module

A Note for Mac OS X Users
-------------------------

Besides `Xcode <http://developer.apple.com/tools/xcode/>`_, you'll also
need an up to date version of MySQL -- we recommend that you not use
the version that is bundled with Mac OS X. The easiest way to install
is via `MacPorts <http://www.macports.org/>`_.

.. sourcecode:: bash

    # If you haven't installed MySQL5 yet, do so via MacPorts:
    $ sudo port install mysql5-server

When it comes time for the MySQL-python bindings to be installed,
the correct ``mysql_config`` file must be on your ``$PATH``:

.. sourcecode:: bash

    # Run this and add it to your ~/.profile
    export PATH=$PATH:/opt/local/bin

    # MacPorts calls this mysql_config5, lets symlink it to mysql_config:
    $ ln -s /opt/local/bin/mysql_config5 /opt/local/bin/mysql_config


Virtual Environments
--------------------

We strongly recommend running MediaCore inside its own ``virtualenv``.
Each virtual environment is compartmentalized, allowing you to run
different versions of the same package for different apps and
situations. It helps keep everything organized and will someday save you
a headache, so if you haven't already, install it now!

.. sourcecode:: bash

   # To install virtualenv:
   $ sudo easy_install virtualenv

   # Or, on Mac OSX with MacPorts:
   $ sudo port -v install py25-virtualenv

Once that's done you can create your new virtual environment:

.. sourcecode:: bash

   # To create a virtual environment:
   $ virtualenv --no-site-packages mediacore_env

   # Or, for Apache+mod_wsgi deployments:
   $ virtualenv mediacore_env

   # Then, to activate that virtual environment:
   $ cd mediacore_env
   $ source bin/activate

Now that you're in a newly created virtual environment, any packages you
install will only be accessible when you've activated the environment as
we just did.

Installing MediaCore and its dependencies
-----------------------------------------

You can get MediaCore by `downloading it from our site
<http://getmediacore.com/download>`_ or, for those familiar with Git
version control, we have a `public Git repository
<http://github.com/simplestation/mediacore/>`_. Git is great because
it makes it easy to stay right up-to-date with bugfixes as they're made.

Here ``setup.py`` downloads and installs all the necessary dependencies
for MediaCore:

.. sourcecode:: bash

   # If you've just downloaded a source distribution:
   $ tar xzvf MediaCore-0.7.2.tar.gz
   $ cd MediaCore-0.7.2
   $ python setup.py develop

   # Or, for developers especially, but anyone familiar with Git:
   $ git clone git://github.com/simplestation/mediacore.git
   $ cd mediacore
   $ python setup.py develop


Configuring Your New Deployment
-------------------------------

The standard with TurboGears/Pylons-based apps is to have a separate ini
config file for each deployment or installation of the app.

If you're just setting up a development machine, we've bundled a config
setup with interactive debugging and such already configured.

In production and staging environments it is important to generate a
config file. This will properly setup unique salts for authentication,
among other things.

.. sourcecode:: bash

   # To create deployment.ini in your current dir:
   $ paster make-config MediaCore deployment.ini

Open it up and have a look through. The default settings should get you
started, only the database needs to be setup, which we'll do in the
next step.

Please note that the ``media_dir`` you've configured must be writable
by the server. Inside the ``image_dir``, make the ``media`` and
``podcasts`` folders writable as well.


Database Setup
--------------

MediaCore comes with a ``setup.sql`` script to populate a database with
tables and some basic data. You'll need to create a database for it,
then import that script. This can be done in a variety of ways, including
phpMyAdmin, CocoaMySQL, or the command line:

.. sourcecode:: bash

   # Import into an already existing database called mediacore:
   $ mysql -u root -p mediacore < setup.sql

You can now edit your INI config file to point to this new database.
Look for the ``sqlalchemy.url`` setting. The format should be pretty
self-explanatory, most users will just have to edit the username,
password and dbname parts.


Launching the Built-in Server
-----------------------------

Now that MediaCore itself is installed and the basics are configured,
we can test it out using the Paste server. It's bundled with TG/Pylons
so you have it already, simply run:

.. sourcecode:: bash

   $ paster serve --reload development.ini

Now open http://localhost:8080/ to see how it works! You can try access
the admin at http://localhost:8080/admin/ with username admin, password
admin. (Remember to `change your password
<http://localhost:8080/admin/settings/users/1>`_!)

If this produces errors then MediaCore or one of its dependencies is not
setup correctly. Please feel free to ask questions and submit solutions
via our `community forums <http://getmediacore.com/>`_.

If this is your development machine, you're good to go. There are
lots of really cool features when debug mode is on (set in the ini
config), like interactive web-based debugging when an exception occurs.
You can view the entire stack trace, with local variables and their
values, and even execute code in any context of the trace. Also,
if you have ipython installed, try calling ``mediacore.ipython()()``
at some point in your code; it'll act as a breakpoint where it opens
an ipython shell with the local scope for you to play with.


Further Steps for Production
----------------------------

The built-in Paste server does a great job for development, but usually
people demand more in production environments. MediaCore is WSGI-based
so there are many possible ways to deploy it.

.. toctree::

   apache-wsgi
   apache-fastcgi

