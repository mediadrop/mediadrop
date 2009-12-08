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

.. note::

   Mac OSX users also require `Xcode
   <http://developer.apple.com/tools/xcode/>`_ (comes on the OSX
   install discs). `MacPorts <http://www.macports.org/>`_ is
   also highly recommended.


By the time you're done installing you will also have:

* The python ``virtualenv`` package
* The python ``MySQLdb`` database adapter
* To run on Apache, the ``mod_wsgi`` module


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

   # However, if this virtualenv is going to be used by Apache+mod_wsgi:
   $ virtualenv mediacore_env

   # To activate that virtual environment:
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

.. note::

   **Mac OS X users** must install certain dependencies manually
   before proceeding:

   .. sourcecode:: bash

      # Test to see if PIL is installed:
      $ python -c "from PIL import Image"

      # If an ImportError is thrown, install:
      $ sudo port install py25-pil

   Leopard comes with a version of MySQL pre-installed, however,
   we recommend installing a newer version via MacPorts. Either way,
   you'll need the Python bindings.

   .. sourcecode:: bash

      # In case you haven't installed MySQL5 yet:
      $ sudo port install mysql5-server

      # Test to see if you have the MySQL-python bindings:
      $ python -c "import MySQLdb"

      # If an ImportError is thrown, install:
      $ sudo port install py25-mysql

   Now when we run ``setup.py``, the libraries it can't install
   properly will be there already, so the setup will complete.

Here, ``setup.py`` downloads and installs all the necessary dependencies
for MediaCore.

.. sourcecode:: bash

   # Coming soon -- install via PyPi -- no download necessary:
   $ easy_install MediaCore

   # If you've just downloaded a source distribution:
   $ tar xzvf MediaCore-0.7.tar.gz
   $ cd MediaCore-0.7
   $ python setup.py develop

   # Or, for developers especially, but anyone familiar with Git:
   $ git clone git://github.com/simplestation/mediacore.git
   $ python setup.py develop


Database Setup
--------------

MediaCore comes with a ``setup.sql`` script to populate a database with
tables and some basic data. You'll need to create a database for it,
then import that script. This can be done through phpMyAdmin, CocoaMySQL,
or the command line:

.. sourcecode:: bash

   # To create an empty database with root:
   $ mysql5 -u root -p < "CREATE DATABASE mediacore;"

   # Then you can actually execute the import:
   $ mysql5 -u root -p < setup.sql

   # If no mysql5 executable is found, try simply mysql instead


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

Now edit your ini config. The most important setting right now is the
``sqlalchemy.url``. The format should be pretty self-explanatory, most
users will just have to edit the username, password and dbname parts.


Launching the Built-in Server
-----------------------------

Now that MediaCore itself is installed and the basics are configured,
we can test it out using the Paste server. It's bundled with TG/Pylons
so you have it already, simply run:

.. sourcecode:: bash

   $ paster serve development.ini

Now open http://localhost:8080/ to see how it works!

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

   apache

