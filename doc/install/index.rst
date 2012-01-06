.. _install_toplevel:

============
Installation
============

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
--------------------

MediaCore CE runs on \*nix operating systems. We've tested CentOS and
Mac OS X, but any Linux or BSD based OS should work just fine.

If you run Windows and want to try MediaCore CE, you have two options:

* If you're an experienced developer, try your hand at translating MediaCore CE
  and its installation process to a Windows environment. It's probably not
  that different. We'd love to hear how you did it.
* Find a cheap web host that offers Apache, FastCGI, and SSH support, and
  install it on there.

**You will need:**

.. include:: requirements-list.rst

The :ref:`install_requirements` page has examples of how to install these
packages on a few different platforms. If you haven't already done so,
go there now.


Step 1: Setup a Python Virtual Environment
------------------------------------------

**NOTE: Past this point, it will be assumed that all packages required in**
`Step 0: Requirements`_ **are installed.**

If you haven't heard of them, `Virtual Environments <http://pypi.python.org/pypi/virtualenv>`_
are a way to keep installations of multiple Python applications from
interfering with each other.

This means you can install MediaCore CE and all of its dependencies without
worrying about overwriting any existing versions of Python libraries.

The following command will create a folder named ``mediacore_env`` in the
current directory. You can put this folder anywhere, but remember where it
is--we'll need to point to it later.

.. sourcecode:: bash

   # Create a new virtual environment:
   virtualenv --no-site-packages mediacore_env

   # Now, activate that virtual environment:
   source mediacore_env/bin/activate


Now that you've activated the newly created virtual environment, any packages
you install will only be accessible when you've activated the environment.

**NOTE: Any time you want to work with MediaCore CE, you should thus activate the
virtual environment as we just did in the line above.**


Step 2: Install MediaCore CE
-------------------------
There are two main ways to get MediaCore CE:

a. **For most users**, you should `download the latest official release of
   Mediacore CE <http://getmediacore.com/download>`_ from our site.

   Once you've downloaded MediaCore CE, it's time to unpack it and install.

   ``setup.py`` will download and install all the necessary dependencies
   for MediaCore CE into your virtual environment:

   .. sourcecode:: bash

      # Unpack the downloaded distribution
      tar xzvf MediaCore-0.9.0.tar.gz
      cd MediaCore-0.9.0

      # Install!
      python setup.py develop

b. **For developers**, or users that are very familiar with Git
   version control, we have a `public Git repository
   <http://github.com/mediacore/mediacore/>`_. Git is great because
   it makes it easy to stay right up-to-date with bugfixes as they're made, and
   you can contribute changes back by `creating your own fork in GitHub
   <http://help.github.com/forking/>`_.

   .. sourcecode:: bash

      # Download and install via Git
      git clone git://github.com/mediacore/mediacore.git
      cd mediacore

      # Install!
      python setup.py develop

**Note:** If running 'python setup.py develop' crashes, you might be having this problem: :ref:`install_trouble_ppc`


Step 3: Create the Database
---------------------------

Here we will create a database for MediaCore CE in MySQL. You can
use phpMyAdmin, CocoaMySQL, `cPanel
<http://www.siteground.com/tutorials/php-mysql/mysql_database_user.htm>`_, the
`mysql command line interface
<http://www.debuntu.org/how-to-create-a-mysql-database-and-set-privileges-to-a-user>`_,
or any other tool you like.

We're going to assume that the database is called ``mediacore``, the mysql
user is called ``mediacore_user``, and the password is ``mysecretpassword``.

For example, via the mysql command line client:

.. sourcecode:: bash

   # Open up the mysql command line interface
   mysql -u root

   # OR: if you get an error like
   # "ERROR: Access denied for user 'root'@'localhost' (using password: NO)"
   # it's probably because your root mysql user has a password. Use -p to enter it.
   mysql -u root -p

.. sourcecode:: mysql

   # Then, inside the mysql shell:

   mysql> create database mediacore;
   Query OK, 1 row affected (0.00 sec)

   mysql> grant usage on mediacore.* to mediacore_user@localhost identified by 'mysecretpassword';
   Query OK, 0 rows affected (0.00 sec)

   mysql> grant all privileges on mediacore.* to mediacore_user@localhost;
   Query OK, 0 rows affected (0.33 sec)

   mysql> exit;
   Bye


Step 4: Preliminary Configuration
---------------------------------

If you're installing on your development machine, we've included a config
file that has things like interactive debugging already configured.

Open up ``development.ini`` and have a look through. The default settings
should get you started. The only line that needs to be edited right away is
the database configuration.

Under the ``[app:main]`` heading, look for the ``sqlalchemy.url`` setting.
It looks like this:

.. sourcecode:: ini

   sqlalchemy.url = mysql://username:pass@localhost/dbname?charset=utf8&use_unicode=0

**Change the "username", "pass", and "dbname"** fields to the username,
password, and database name you used in Step 3. For example:

.. sourcecode:: ini

   sqlalchemy.url = mysql://mediacore_user:mysecretpassword@localhost/mediacore?charset=utf8&use_unicode=0

**NOTE 1:** For Uploads to work, the directory pointed to by the ``media_dir``
setting must be writable by your user.

**NOTE 2:** For Uploads to work, the ``media`` and ``podcasts`` folders inside
the directory pointed to by the ``image_dir`` setting must also be writable by
your user.


Step 5: Populate the Database
-----------------------------

First, The creation of all database tables and addition of initial data is
taken care of via this Pylons command:

.. sourcecode:: bash

   paster setup-app development.ini

Second, If you want to enable the fulltext searching shown on the demo site, you will
need to have access to the root account for your MySQL database. Some shared
hosts don't allow this, so we have made this feature optional. To set up the
triggers that enable fulltext searching, import ``setup_triggers.sql`` like so:

.. sourcecode:: bash

   # Import fulltext search database triggers
   mysql -u root mediacore < setup_triggers.sql

**NOTE:** If you do not import ``setup_triggers.sql``, MediaCore CE's search
will always return no results. You can easily disable this feature in your
installation by removing the search form from
``/path/to/mediacore_install/mediacore/templates/nav.html``.
In a future release, we plan to design search so that it doesn't require
MySQL's root account.


Step 6: Launch the Built-in Server
----------------------------------

Now that MediaCore CE itself is installed and the basics are configured,
we can test it out using the Paste server. It's bundled with Pylons
so you have it already, simply run:

.. sourcecode:: bash

   paster serve --reload development.ini

Now open http://localhost:8080/ to see how it works! You can try access
the admin at http://localhost:8080/admin/ with **username: admin, password:
admin**. (Remember to `change your password
<http://localhost:8080/admin/settings/users/1>`_!)

If this produces errors then MediaCore CE or one of its dependencies is not
setup correctly. Please feel free to ask questions and submit solutions
via our `community forums <http://getmediacore.com/>`_.

If this is your development machine, you're good to go.


.. _production_deployments:

Step 7: Production Deployments
------------------------------

If you want to access MediaCore CE from other computers, you'll need to set up a
production config.

**Production Config:**
   On your production deployment, you'll want to disable debugging, set up unique
   password salts, and maybe change some other settings. To do this, you can
   create a second config file named ``deployment.ini`` with the following one
   line command:

   .. sourcecode:: bash

      # To create deployment.ini in your current dir:
      paster make-config MediaCore CE deployment.ini

   Then edit ``deployment.ini`` as you did for ``development.ini`` (e.g. set
   up the database config line).

**Permissions:**
   Usually, when deploying using a production server, the user that runs the
   server will not be the user account that installs the software. You need
   to ensure that your server user can write to all of the directories inside
   ``/path/to/mediacore_installs/data``.

**Production Server:**
   MediaCore CE is WSGI-based so there are many possible ways to deploy it.
   The built in Paste server does a great job for development, but you
   may want to run MediaCore CE from a more performant webserver.
   Below are three methods you can use to deploy MediaCore CE:

a. ``mod_fastcgi`` is simplest and will work with most shared hosting
   environments, so long as the server has ``mod_fastcgi`` installed.

   .. toctree::

       apache-fastcgi

b. ``mod_wsgi`` requires root access on your server, but can be tuned
   for better performance than ``mod_fastcgi``.

   .. toctree::

       apache-wsgi

c. ``uwsgi`` requires root access on your server, but provides significant
   performance benefits including page speed and reduced memory usage.

    .. toctree::

       nginx-uwsgi

