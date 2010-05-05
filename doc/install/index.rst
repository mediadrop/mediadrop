.. _install_toplevel:

============
Installation
============

This is a full walkthrough of how to get MediaCore running.

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

MediaCore runs on \*nix operating systems. We've tested CentOS and
Mac OS X, but any Linux or BSD based OS should work just fine.

If you run Windows and want to try MediaCore, you have two options:

* If you're an experienced developer, try your hand at translating MediaCore
  and its installation process to a Windows environment. It's probably not
  that different. We'd love to hear how you did it.
* Find a cheap web host that offers Apache, FastCGI, and SSH support, and
  install it on there.

**You will need:**

* Python 2.5.x or newer
* MySQL 5.0.x or newer
* `GCC <http://en.wikipedia.org/wiki/GNU_Compiler_Collection>`_  must be
  installed and available on your ``$PATH`` for certain required Python
  packages to install properly.

**You may need** (if you don't have permissions to install new software on
the server you're using, you'll also need to have the following packages
installed):

* `Python setuptools <http://pypi.python.org/pypi/setuptools>`_
* `Python virtualenv <pypi.python.ort/pypi/virtualenv>`_

If you do have permissions to install new software, we'll cover
the installation of ``setuptools`` and ``virtualenv`` in
`Step 0.2: Installing Setuptools`_ and
`Step 0.3: Installing Virtualenv`_ below.


Step 0.1.0: Requirements Installation on OS X
---------------------------------------------

As mentioned above, you need to have GCC installed for some of MediaCore's
dependencies to be able to compile. For Mac OS X users, that means installing
`Xcode <http://developer.apple.com/tools/xcode/>`_.

You can install Xcode from your OS X install CD, from the "Optional Installs"
directory, or (if you have OSX 10.5.8 or 10.6) you can download it from the
above link.

For the MySQL and Python requirements, we recommend using `MacPorts <http://www.macports.org/>`_.
Mac OS X ships with a version of Python installed, but we find it is
simpler and more reliable to have your own version installed in a separate
place. Macports will (by default) install packages to ``/opt/local``, keeping itself
completely separate from any previously installed packages that OS X needs to
function.

After you have Xcode installed, You can install MacPorts by downloading the
dmg disk image from `MacPorts install page <http://www.macports.org/install.php>`_
and running the contained installer.

To install MySQL 5 and Python 2.5 once MacPorts is installed, open up a
terminal (like Terminal.app or iTerm.app) and enter the following commands:

.. sourcecode:: bash

    # By this point you should have Xcode and MacPorts installed...
    # Make sure your MacPorts files are up to date
    sudo port selfupdate

    # Load the updated environment settings (make sure the installed MacPorts
    # executables will be on your $PATH.)
    source ~/.profile

    # Install MySQL5 and Python2.5
    sudo port install mysql5-server python25

    # Initialize the newly installed MySQL server
    sudo /opt/local/lib/mysql5/bin/mysql_install_db --user=mysql

    # Start the MySQL Server and instruct it to start every time you reboot
    sudo launchctl load -w /Library/LaunchDaemons/org.macports.mysql5.plist

    # NOTE: If you ever want to stop the MySQL Server, run the following command:
    #   sudo launchctl unload -w /Library/LaunchDaemons/org.macports.mysql5.plist

    # Put a link to mysql_config where other programs will expect to find it
    sudo ln -s /opt/local/bin/mysql_config5 /opt/local/bin/mysql_config

    # Put a link to mysql client for consistency in naming with other platforms
    sudo ln -s /opt/local/bin/mysql5 /opt/local/bin/mysql

Step 0.1.1: Requirements Installation on Ubuntu 9.04
----------------------------------------------------

You're in luck! GCC and mysql-server-5.0 are installed by default on Ubuntu
9.04. You'll just have to install mysql-client and python2.5 (and their
respective libraries). Then you can proceed with installing Setuptools and
Virtualenv as below.

.. sourcecode:: bash

   # install the mysql client and python2.5
   sudo apt-get install mysql-client-5.1 libmysqlclient15off python2.5-dev python2.5-doc


Step 0.2: Installing Setuptools
-------------------------------

The Python setuptools package is what we'll use to automate the rest of the
installation of Python packages.

First, check that you have setuptools installed for Python2.5:

.. sourcecode:: bash

   # Check if you have setuptools installed:
   python2.5 -c 'import setuptools'

If you get no error, you can skip the rest of this step; setuptools is already
installed!

If you get an error like the following, you'll need to install setuptools first:

.. sourcecode:: text

   Traceback (most recent call last):
     File "<string>", line 1, in <module>
   ImportError: No module named setuptools

If you're using a system with a package manager and you know how to install
setuptools 0.6c9 or higher for python2.5 using that package manager go ahead:

.. sourcecode:: bash

   # For example, on Ubuntu 9.04
   sudo apt-get install python-setuptools

   # Or on Mac OS X (with MacPorts):
   sudo port -v install py25-setuptools

Otherwise, download the setuptools installer and install manually:

.. sourcecode:: bash

   # Download the Setuptools installer
   wget http://pypi.python.org/packages/2.5/s/setuptools/setuptools-0.6c11-py2.5.egg

   # Install setuptools
   sudo sh setuptools-0.6c11-py2.5.egg


Step 0.3: Installing Virtualenv
-------------------------------

First, check if you have virtualenv installed.

.. sourcecode:: bash

   # Check if you have virtualenv installed:
   python2.5 -c 'import virtualenv'

If you get no error, you can skip the rest of this step; virtualenv is already
installed!

If you get an error like the following, you'll need to install virtualenv.

.. sourcecode:: text

   Traceback (most recent call last):
     File "<string>", line 1, in <module>
   ImportError: No module named virtualenv

If you're using a system with a package manager and you know how to install
setuptools 0.6c9 or higher for python2.5 using that package manager go ahead:

.. sourcecode:: bash

   # For example, on Ubuntu 9.04, you must install python-virtualenv, then
   # create a custom virtualenv-2.5 script to use with python2.5
   sudo apt-get install python-virtualenv
   sudo cp /usr/bin/virtualenv /usr/bin/virtualenv-2.5
   sudo sh -c "sed 's:#\!/usr/bin/python$:#\!/usr/bin/python2.5:' /usr/bin/virtualenv > /usr/bin/virtualenv-2.5"

   # Or on Mac OS X (with MacPorts):
   sudo port -v install py25-virtualenv

Otherwise, install virtualenv via setuptools:

.. sourcecode:: bash

   # Install virtualenv via setuptools.
   sudo easy_install-2.5 virtualenv


Step 1: Setup a Python Virtual Environment
------------------------------------------

**NOTE: Past this point, it will be assumed that all packages required in**
`Step 0: Requirements`_ **are installed.**

If you haven't heard of them, `Virtual Environments <http://pypi.python.org/pypi/virtualenv>`_
are a way to keep installations of multiple Python applications from
interfering with each other.

This means you can install MediaCore and all of its dependencies without
worrying about overwriting any existing versions of Python libraries.

The following command will create a folder named ``mediacore_env`` in the
current directory you can put this folder anywhere, but remember where it
is--we'll need to point to it later.

.. sourcecode:: bash

   # Create a new virtual environment:
   virtualenv-2.5 --no-site-packages mediacore_env

   # Now, activate that virtual environment:
   source mediacore_env/bin/activate


Now that you've activated the newly created virtual environment, any packages
you install will only be accessible when you've activated the environment.

**NOTE: Any time you want to work with mediacore, you should thus activate the
virtual environment as we just did in the line above.**


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
      tar xzvf MediaCore-0.8.tar.gz
      cd MediaCore-0.8

      # Install!
      python2.5 setup.py develop

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
      python2.5 setup.py develop


Step 3: Setup the Database
--------------------------

The first step here is to create a database for MediaCore in MySQL. You can
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

The second step is to create all the tables and starting data for the
database. All of the information is in ``setup.sql``, so you can load it
with a one line command, like so:

.. sourcecode:: bash

   # Import initial data into an existing database named mediacore:
   mysql -u mediacore_user -p mediacore < setup.sql


If you want to enable the fulltext searching shown on the demo site, you will
need to have access to the root account for your MySQL database. Some shared
hosts don't allow this, so we have made this feature optional. To set up the
triggers that enable fulltext searching, import ``setup_triggers.sql`` like so:

.. sourcecode:: bash

   # Import fulltext search database triggers
   mysql -u root mediacore < setup_triggers.sql

**NOTE:** If you do not import ``setup_triggers.sql``, MediaCore's search
will always return no results. You can easily disable this feature in your
installation by removing the search form from
``/path/to/mediacore_install/mediacore/templates/nav.html``.
In a future release, we plan to design search so that it doesn't require
MySQL's root account.


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


Step 5: Launch the Built-in Server
----------------------------------

Now that MediaCore itself is installed and the basics are configured,
we can test it out using the Paste server. It's bundled with TG/Pylons
so you have it already, simply run:

.. sourcecode:: bash

   paster serve --reload development.ini

Now open http://localhost:8080/ to see how it works! You can try access
the admin at http://localhost:8080/admin/ with **username: admin, password:
admin**. (Remember to `change your password
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

   Then edit ``deployment.ini`` as you did for ``development.ini`` (e.g. set
   up the database config line).

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

