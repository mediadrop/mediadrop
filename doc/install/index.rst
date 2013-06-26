.. _install_toplevel:

************
Installation
************

This is a full walkthrough of how to get MediaCore CE running.

Experienced `Pylons <http://pylonshq.com/>`_
users can check out the :ref:`install_overview` page for a (very) condensed
version of the instructions.

This installation guide assumes a basic familiarity with a \*nix shell.
Experience with a Windows or DOS shell will translate pretty easily.
You should be familiar with the concepts important to web development such as
databases, web servers, and file permissions.
You should be comfortable with running commands in a terminal, and the basics
like ``cd``, ``ls``, ``mkdir``, ``tar``, ``sudo``, etc. For a quick refresher
check out this `introduction to \*nix command shells
<http://vic.gedris.org/Manual-ShellIntro/1.2/ShellIntro.pdf>`_.

Step 0: Requirements
====================

MediaCore CE runs on \*nix operating systems. We've tested CentOS and
Mac OS X, but any Linux or BSD-based OS should work just fine.

If you run Windows and want to try MediaCore CE, you have two options:

- If you're an experienced developer, try your hand at translating MediaCore CE
  and its installation process to a Windows environment. It's probably not
  that different. We'd love to hear how you did it.
- Find a cheap web host that offers Apache, FastCGI, and SSH support, and
  install it on there.

**You will need:**

* Python 2.x (2.4.x or newer)
* a MySQL (5.0.x or newer) or PostgreSQL database
* `GCC <http://en.wikipedia.org/wiki/GNU_Compiler_Collection>`_  must be
  installed and available on your ``$PATH`` for certain required Python
  packages (mysql-python, Pillow) to install properly.
* development headers for Python, libjpeg, zlib, and freetype are also required
  for certain required Python packages (Pillow) to install properly.
* `setuptools <http://pypi.python.org/pypi/setuptools>`_
* `virtualenv <http://pypi.python.ort/pypi/virtualenv>`_

MediaCore CE works with MySQL and PostgreSQL but so far MySQL-based setups have
way more popularity (and some features like the DB-based full-text search are
not yet available for PostgreSQL). Therefore the following install docs assume
you want to work with a MySQL database. If you're going with PostgreSQL you 
should also install the necessary Python PostgreSQL bindings (e.g. psycopg2) and
development headers.

Installing the required dependencies on Linux requires root access (use ``sudo``
or ``su``). In a shared hosting environment usually you can only hope that all
required packages are present.

On Linux you should use the packages of your distribution: Do not try to compile
Python, MySQL or Apache yourself! Doing so (and maintaining a secure system over
years) is a highly challenging task. If you experience problems during the 
install on a well-known Linux distribution the problem is likely not due to 
package versions so self-compiling will not solve the problem!


Below you can find detailed install instructions for some of the most popular 
operating systems. However MediaCore CE will run on other platforms as well
as long as you have a working compiler and the necessary development headers.

.. toctree::
   :maxdepth: 1

   centos-fedora.rst
   debian-ubuntu.rst
   mac-os.rst


Database
-----------------------------------------

Later on your MediaCore install needs a database so it can store data. As 
mentioned before this documentation uses a MySQL database though PostgreSQL 
should work as well.

Please make sure you have credentials to access the MySQL server and an empty 
database. In a shared hosting environment there is usually a web panel to manage
these. If you installed the MySQL server yourself, please create a MySQL user
and a new database.


Install Location
-----------------------------------------

If you are only interested in a development setup (without a permanent 
deployment using a web server, using "paster") this does not have to concern 
you. Just find a folder which will contain the source code and the data files.

For a permanent deployment however you need a folder which is accessible by your
web server. Usually a place below ``/var/www`` is a good choice. 

Ideally the folder is not below the default docroot (often called ``html`` or 
``httpdocs``) but right next to it (sometimes called ``shareddata``). This 
ensures that the web server will never reveal your actual MediaCore source code 
or the configuration files to web users in case of a configuration error.

After step 3 you should have a directory which contains the folders ``data``,
``MediaCore-0.10.0`` (or whatever you named the directory with the MediaCore 
source code), and ``venv`` as well as the ``production.ini`` file.


.. _install_setup_virtualenv:

Step 1: Setup a Python Virtual Environment
==========================================

**NOTE: Past this point, it will be assumed that all packages required in**
`Step 0: Requirements`_ **are installed.**

If you haven't heard of them, `Virtual Environments <http://pypi.python.org/pypi/virtualenv>`_
are a way to keep installations of multiple Python applications from
interfering with each other. This means you can install MediaCore CE and all of 
its dependencies without worrying about overwriting any existing versions of 
Python libraries.

The following command will create a folder named ``venv`` in the
current directory. You can put this folder anywhere, but remember where it is – 
we'll need to point to it later.

.. sourcecode:: bash

   # Create a new virtual environment:
   virtualenv --distribute --no-site-packages venv

   # Now, activate that virtual environment:
   source venv/bin/activate

Now that you've activated the newly created virtual environment, any packages
you install will only be accessible when you've activated the environment.

**NOTE: Any time you want to work with MediaCore CE, you should thus activate the
virtual environment as we just did in the line above.**


Step 2: Install MediaCore CE
============================

There are two main ways to get MediaCore CE:

a. You can `download the latest official release of MediaCore CE <http://mediacorecommunity.org/download>`_ from our site.

   Once you've downloaded MediaCore CE, it's time to unpack it and install.

   ``setup.py`` will download and install all the necessary dependencies
   for MediaCore CE into your virtual environment:

   .. sourcecode:: bash

      # Unpack the downloaded distribution
      tar xzvf MediaCore-0.10.0.tar.gz
      cd MediaCore-0.10.0

      # Install!
      python setup.py develop
      cd ..

b. **For developers and power users** we recommend using the source code 
   directly from our `public git repository <http://github.com/mediacore/mediacore-community/>`_.
   A git deployment makes it easy to track local changes and experienced 
   developers can also stay right up-to-date with bugfixes as they're made.

   .. sourcecode:: bash

      # Download and install via Git
      git clone git://github.com/mediacore/mediacore-community.git mediacore-git
      cd mediacore-git
      
      # now you have the latest development version. For a production deployment
      # you should switch to a release version, e.g.
      git checkout v0.10.0

      # Install!
      python setup.py develop
      cd ..


Step 3: Basic Configuration File
================================

Next we generate a configuration file named ``deployment.ini`` which contains
basic MediaCore settings.

   .. sourcecode:: bash

      # To create deployment.ini in your current dir:
      paster make-config MediaCore deployment.ini

Open up ``deployment.ini`` and have a look through. The default settings
should get you started. The only line that needs to be edited right away is
the database configuration.

Under the ``[app:main]`` heading, look for the ``sqlalchemy.url`` setting.
It looks like this:

.. sourcecode:: ini

   sqlalchemy.url = mysql://username:pass@localhost/dbname?charset=utf8&use_unicode=0

**Change the "username", "pass", and "dbname"** fields to your username,
password, and database name. For example:

.. sourcecode:: ini

   sqlalchemy.url = mysql://mediacore_user:mysecretpassword@localhost/mediacore?charset=utf8&use_unicode=0


Developers should also set ``debug = true`` in the config file but be aware that
this is a security risk in a publicly accessible deployment. 
Also ``db.check_for_leaked_connections = True`` (in ``[app:main]``) might give 
you important warnings on the console.


Step 4: Load Initial Data
=============================

First we need to set up the directory which contains all the file content. Copy
the ``data`` folder from your MediaCore source code next to the 
``production.ini`` file.

.. sourcecode:: bash

   cp -a MediaCore-0.10.0/data .

**NOTE:** For uploads to work, the data directory must be writable by the user
running MediaCore.


The creation of all database tables and addition of initial data is taken care 
of via this Pylons command:

.. sourcecode:: bash

   paster setup-app deployment.ini

If you want to enable simple fulltext searching, you will need to have access 
to the root account for your MySQL database. Some shared hosts don't allow 
this, so we have made this feature optional. To set up the triggers that 
enable fulltext searching, import ``setup_triggers.sql`` like so:

.. sourcecode:: bash

   # Import fulltext search database triggers
   mysql -u root mediacore < MediaCore-0.10.0/setup_triggers.sql

**NOTE:** If you do not import ``setup_triggers.sql``, MediaCore CE's search
will only search for exact matches in the media title (e.g. searching for 
"smith live" will find not find a media named "Joe Smith: live performance").
In a future release, we plan to release optional plugins to use 
a database-independent search engine.


Step 5: Launch the Built-in Server
==================================

Now that MediaCore CE itself is installed and the basics are configured,
we can test it out using the Paste server. It's bundled with Pylons
so you have it already, simply run:

.. sourcecode:: bash

   paster serve --reload deployment.ini

Now open http://localhost:8080/ to see how it works! You can try access
the admin at http://localhost:8080/admin/ with **username: admin, password:
admin**. (Remember to `change your password
<http://localhost:8080/admin/settings/users/1>`_!)

If this produces errors then MediaCore CE or one of its dependencies is not
setup correctly. Please feel free to ask questions and submit solutions
via our `community forums <http://mediacorecommunity.org/community>`_.

If this is your development machine, you're good to go.


.. _production_deployments:

Step 6: Production Deployments
==============================

MediaCore CE is WSGI-based so there are many possible ways to deploy it.
The built in Paste server does a great job for development, but you may want 
to run MediaCore CE from a more performant webserver. Below are three methods 
you can use to deploy MediaCore CE:

- :doc:`Apache/mod_fcgid <apache-fastcgi>` (FastCGI) is simplest and will work 
  with most shared hosting environments, so long as the server has 
  ``mod_fcgid`` installed.
- :doc:`Apache/mod_wsgi <apache-wsgi>` is preferred way of deploying Python 
  applications like MediaCore CE and can be tuned for better performance than 
  ``mod_fastcgi``.
- :doc:`nginx / uwsgi <nginx-uwsgi>` is an expert option which can provide significant 
  performance benefits when serving static files.

If possible please use ``mod_wsgi`` as this mode is tested best and is likely
the easiest to configure for new users.


