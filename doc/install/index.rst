.. _install_toplevel:

============
Installation
============

This is a full walkthrough of how to get Virtualenv / TurboGears / MediaCore
running.

Experienced TG2 users can check out the :ref:`install_overview` page for a
(very) condensed version of the instructions.

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

You will also need:

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

To install MySQL 5 and Python 2.5 once MacPorts is installed:

.. sourcecode:: bash

    # Add the MacPorts executable path to your $PATH:
    export PATH=$PATH:/opt/local/bin

    # Ensure that it's always on your $PATH
    echo "export PATH=\$PATH:/opt/local/bin" > ~/.profile

    # Install MySQL5 and Python2.5
    sudo port install mysql5-server python25

    # Put a link to mysql_config where other programs will expect to find it
    ln -s /opt/local/bin/mysql_config5 /opt/local/bin/mysql_config


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

You can get MediaCore by `downloading it from our site
<http://getmediacore.com/download>`_ or, for those familiar with Git
version control, we have a `public Git repository
<http://github.com/simplestation/mediacore/>`_. Git is great because
it makes it easy to stay right up-to-date with bugfixes as they're made.

Here ``setup.py`` downloads and installs all the necessary dependencies
for MediaCore:

.. sourcecode:: bash

   # If you've just downloaded a source distribution:
   tar xzvf MediaCore-0.7.2.tar.gz
   cd MediaCore-0.7.2
   python setup.py develop

   # Or, for developers especially, but anyone familiar with Git:
   git clone git://github.com/simplestation/mediacore.git
   cd mediacore
   python setup.py develop


Step 3: Setup the Database
--------------------------

MediaCore comes with a ``setup.sql`` script to populate a database with
tables and some basic data. You'll need to create a database for it,
then import that script. This can be done in a variety of ways, including
phpMyAdmin, CocoaMySQL, or the command line:

.. sourcecode:: bash

   # Import into an already existing database called mediacore:
   mysql -u root -p mediacore < setup.sql

You can now edit your INI config file to point to this new database.
Look for the ``sqlalchemy.url`` setting. The format should be pretty
self-explanatory, most users will just have to edit the username,
password and dbname parts.


Step 4: Preliminary Configuration
---------------------------------

The standard with TurboGears/Pylons-based apps is to have a separate ini
config file for each deployment or installation of the app.

If you're just setting up a development machine, we've bundled a config
setup with interactive debugging and such already configured.

In production and staging environments it is important to generate a
config file. This will properly setup unique salts for authentication,
among other things.

.. sourcecode:: bash

   # To create deployment.ini in your current dir:
   paster make-config MediaCore deployment.ini

Open it up and have a look through. The default settings should get you
started, only the database needs to be setup, which we'll do in the
next step.

Please note that the ``media_dir`` you've configured must be writable
by the server. Inside the ``image_dir``, make the ``media`` and
``podcasts`` folders writable as well.


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



Further Steps for Production
----------------------------

The built-in Paste server does a great job for development, but usually
people demand more in production environments.

MediaCore is WSGI-based so there are many possible ways to deploy it.
Below are two of the most popular methods:

``mod_fastcgi`` is simplest and will work with most shared hosting
environments, so long as the server has ``mod_fastcgi`` installed.

.. toctree::

    apache-fastcgi

``mod_wsgi`` requires root access on your server, but can be tuned
for better performance than ``mod_fastcgi``.

.. toctree::

   apache-wsgi

