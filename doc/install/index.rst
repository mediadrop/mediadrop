.. _install_toplevel:

============
Installation
============

This is a full walkthrough of how to get MediaCore running.

Experienced TG2 users can check out the :ref:`install_overview` page for a
(very) condensed version of the instructions.

Step 0: Requirements
--------------------

TODO: Explain that we expect a basic fluency with the \*nix shell, cd, ls, mkdir, tar, etc.
provide a link to an intro to that stuff.

MediaCore runs on \*nix operating systems. We've tested CentOS and
Mac OS X, but any Linux or BSD based OS should work just fine.

If you run Windows and want to try MediaCore, you have two options:

* If you're an experienced developer, try your hand at translating MediaCore
  and its installation process to a Windows environment. It's probably not
  that different. We'd love to hear how you did it.
* Find a cheap web host that offers Apache, FastCGI, and SSH support, and
  install it on there.

**You will also need:**

* Python 2.5.x or newer
* MySQL 5.0.x or newer
* GCC must be installed and available on your ``$PATH`` for certain required
  Python packages to install properly.


Step 0.1: Requirements Installation on OS X
-------------------------------------------

As mentioned above, you need to have GCC installed for some of MediaCore's
dependencies to be able to compile. For Mac OS X users, that means installing
`Xcode <http://developer.apple.com/tools/xcode/>`_.

For the MySQL and Python requirements, we recommend using `MacPorts <http://www.macports.org/>`_.
Mac OS X ships with versions of MySQL and Python installed, but we find it is
simpler and more reliable to have your own versions installed in a separate
place. Macports will (by default) install packages to ``/opt/local``, keeping itself
completely separate from any previously installed packages that OS X needs to
function.

TODO: Explain how to install macports, and note that you'll have to port selfupdate or something. check with stuart.

To install MySQL 5 and Python 2.5 once MacPorts is installed, open up a
terminal (like Terminal.app or iTerm.app) and enter the following commands:

.. sourcecode:: bash

    # Add the MacPorts executable path to your $PATH:
    export PATH=$PATH:/opt/local/bin

    # Ensure that it's always on your $PATH
    echo "export PATH=\$PATH:/opt/local/bin" > ~/.profile

    # Install MySQL5 and Python2.5
    sudo port install mysql5-server python25

    # Start the MySQL Server running in the background
    # This will print some numbers to show that it started successfully
    # TODO: Apparently this doesn't work with the stock macports on osx 10.6 urgh.
    sudo /opt/local/bin/mysqld_safe5 &

    # Put a link to mysql_config where other programs will expect to find it
    sudo ln -s /opt/local/bin/mysql_config5 /opt/local/bin/mysql_config


Step 1: Setup a Python Virtual Environment
------------------------------------------

If you haven't heard of them, Virtual Environments are a way to keep
installations of multiple Python applications from interfering with each
other.

This means you can install MediaCore and all of its dependencies without
worrying about overwriting any existing versions of Python libraries.

.. sourcecode:: bash

   # Check if you have virtualenv installed:
   virtualenv

   # If you get an error like the following, you'll need to install it:
   # -bash: virtualenv: command not found

   # To install virtualenv:
   sudo easy_install virtualenv

   # Or, on Mac OS X with MacPorts:
   sudo port -v install py25-virtualenv

Once that's done you can create your new virtual environment. The following
command will create a folder named ``mediacore_env`` in the current directory.
You can put this folder anywhere, but remember where it is--we'll need to
point to it later.

.. sourcecode:: bash

   # Create a new virtual environment:
   virtualenv --no-site-packages mediacore_env

   # Now, activate that virtual environment:
   source mediacore_env/bin/activate


Now that you've activated the newly created virtual environment, any packages
you install will only be accessible when you've activated the environment as
we just did in the line above.


Step 2: Install MediaCore
-------------------------
There are two main ways to get MediaCore:

a. **For most users**, you should `download the latest official release of
   Mediacore <http://getmediacore.com/download>`_ from our site.

   Once you've downloaded MediaCore, it's time to unpack it and install.

   ``setup.py`` will download and install all the necessary dependencies
   for MediaCore into your virtual environment:

   .. sourcecode:: bash

      # Unpack the downloaded distribution
      tar xzvf MediaCore-0.7.2.tar.gz
      cd MediaCore-0.7.2

      # Install!
      python setup.py develop

b. **For developers**, or users that are very familiar with Git
   version control, we have a `public Git repository
   <http://github.com/simplestation/mediacore/>`_. Git is great because
   it makes it easy to stay right up-to-date with bugfixes as they're made, and
   you can contribute changes back by `creating your own fork in GitHub
   <http://help.github.com/forking/>`_.

   .. sourcecode:: bash

      # Download and install via Git
      git clone git://github.com/simplestation/mediacore.git
      cd mediacore

      # Install!
      python setup.py develop


Step 3: Setup the Database
--------------------------

The first step here is to create a database for MediaCore in MySQL. You can
use phpMyAdmin, CocoaMySQL, `cPanel
<http://www.siteground.com/tutorials/php-mysql/mysql_database_user.htm>`_, the
`mysql command line interface
<http://www.debuntu.org/how-to-create-a-mysql-database-and-set-privileges-to-a-user>`_,
or any other tool you like.

We're going to assume that the database is called ``mediacore`` and the mysql
user is called ``mediacore_user``.

The second step is to create all the tables and starting data for the
database. All of the information is in ``setup.sql``, so you can load it
with a one line command, like so:

.. sourcecode:: bash

   # Import initial data into an existing database named mediacore:
   mysql -u mediacore_user -p mediacore < setup.sql


Step 4: Preliminary Configuration
---------------------------------

If you're installing on your development machine, we've included a config
file that has things like interactive debugging already configured.

Open up ``development.ini`` and have a look through. The default settings
should get you started. The only line that needs to be edited right away is
the database configuration.

Look for the ``sqlalchemy.url`` setting. Change the ``username``, ``pass``,
and ``dbname`` to the username, password, and database name you used in
Step 3.

**NOTE 1:** For Uploads to work, the directory pointed to by ``media_dir``
must be writable by the server.

**NOTE 2:** For Uploads to work, the ``media`` and ``podcasts`` folders inside
the directory pointed to by ``image_dir`` must also be writable by the server.


Step 5: Launch the Built-in Server
----------------------------------

Now that MediaCore itself is installed and the basics are configured,
we can test it out using the Paste server. It's bundled with TG/Pylons
so you have it already, simply run:

.. sourcecode:: bash

   paster serve --reload development.ini

Now open http://localhost:8080/ to see how it works! You can try access
the admin at http://localhost:8080/admin/ with username admin, password
admin. (Remember to `change your password
<http://localhost:8080/admin/settings/users/1>`_!)

If this produces errors then MediaCore or one of its dependencies is not
setup correctly. Please feel free to ask questions and submit solutions
via our `community forums <http://getmediacore.com/>`_.

If this is your development machine, you're good to go.



Step 6: Production Deployments
------------------------------

The built-in Paste server does a great job for development, but usually
people demand more in production environments.

**Production Config:**
   On your production deployment, you'll want to disable debugging, set up unique
   password salts, and maybe change some other settings. To do this, you can
   create a second config file named ``deployment.ini`` with the following one
   line command:

   .. sourcecode:: bash

      # To create deployment.ini in your current dir:
      paster make-config MediaCore deployment.ini

**Production Server:**
   MediaCore is WSGI-based so there are many possible ways to deploy it.
   Below are two of the most popular methods:

a. ``mod_fastcgi`` is simplest and will work with most shared hosting
   environments, so long as the server has ``mod_fastcgi`` installed.

   .. toctree::

       apache-fastcgi

b. ``mod_wsgi`` requires root access on your server, but can be tuned
   for better performance than ``mod_fastcgi``.

   .. toctree::

      apache-wsgi

