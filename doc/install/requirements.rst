.. _install_requirements:

=====================================
Preliminary Requirements Installation
=====================================

MediaCore CE is dependent on a number of packages being available on your system.
This page has examples of how to install them on a few different platforms.

.. include:: requirements-list.rst

Although Python versions 2.4 to 2.7 are supported, the examples in this guide
will use python 2.7 whenever a version must be specified.


Step 1a: First Requirements in Mac OS X
---------------------------------------

You will need to have GCC installed for some of MediaCore CE's dependencies
to install correctly. For Mac OS X users, that means installing
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

To install MySQL 5 and Python 2.7 once MacPorts is installed, open up a
terminal (like Terminal.app or iTerm.app) and enter the following commands:

.. sourcecode:: bash

    # By this point you should have Xcode and MacPorts installed...
    # Make sure your MacPorts files are up to date
    sudo port selfupdate

    # Load the updated environment settings (make sure the installed MacPorts
    # executables will be on your $PATH.)
    source ~/.profile

    # Install MySQL5 and Python2.7
    sudo port install mysql5-server python27

    # Make Python2.7 the default version
    sudo pythonselect 2.7

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

Now you can proceed with :ref:`installing_setuptools`.


Step 1b: First Requirements in Ubuntu 10.04+
--------------------------------------------

GCC is installed by default on Ubuntu. You'll just have to install mysql and
python (and their respective libraries).

.. sourcecode:: bash

   # install the mysql client and python-dev
   sudo apt-get install mysql-server mysql-client libmysqlclient-dev python-dev python-doc

   # install the necessary libraries for creating thumbnails
   sudo apt-get install libjpeg-dev libjpeg62 libjpeg62-dev zlib1g-dev libfreetype6 libfreetype6-dev

Now you can proceed with :ref:`installing_setuptools`.

Step 1c: First Requirements in CentOS/RHEL 5.x
----------------------------------------------

Depending on how you configured your CentOS Distro at install time you may need
to install the following packages:
  * GCC
  * make
  * autoconf
  * automake

Just to be safe, run the following command to install any missing packages.
Don't worry if you have some packages installed already as running the command
will only install the ones you need, and will leave the existing ones alone.

.. sourcecode:: bash

   # install the necessary libraries for compiling
   sudo yum install gcc make autoconf automake

System Libraries

You will also need to make sure certain system libraries are installed.
Running the following command will install any libraries that are missing.

.. sourcecode:: bash

    # install any missing system libraries
    sudo yum install libjpeg libjpeg-devel zlib zlib-devel freetype freetype-devel

MySQL Requirements

If you already have a working MySQL installation you are going to use, then feel
free to skip this section. Otherwise you will need to install MySQL. You can
install MySQL any way that you like, but we recommend a yum installation as it
will keep things consistent and easier to maintain.

You'll need to install the MySQL client, server and development libraries:

.. sourcecode:: bash

    # install MySQL server, client and libraries
    sudo yum install mysql mysql-server mysql-devel

MySQL should now be installed, and by default configured to start when your
system starts. To verify this, you can run the following comand:

.. sourcecode:: bash

    # verify MySQL is configured to survive reboots
    sudo chkconfig --list mysql

You should see the output from chkconfig similar to this:

.. sourcecode:: bash

    # sample output from chkconfig --list mysql
    mysql        0:off        1:off        2:off        3:on        4:on        5:on        6:off

If you don't see this output you will need to install the MySQL control script,
and add MySQL to chkconfig:

.. sourcecode:: bash

    # copy default MySQL control script into init.d
    sudo cp /usr/share/mysql/mysql.server /etc/rc.d/init.d/mysql

    # add MySQL with chkconfig
    sudo chkconfig --add mysql

    # enable MySQL for runlevels 3,4,5 with chkconfig
    sudo chkconfig --levels 345 mysql on

At this point you should be all set to start your MySQL server:

.. sourcecode:: bash

    # start MySQL via service
    sudo service mysql start

    or

    # start mysql via mysqld_safe
    sudo mysqld_safe &

Python Requirements

MediaCore CE supports Python versions 2.4 and up. CentOS/RHEL 5.x ships with
Python 2.4, so you should be OK with the system default as a base for your
operations.

Now you can proceed with installing Setuptools and Virtualenv as below.


.. _installing_setuptools:

Step 2: Installing Setuptools
-----------------------------

The Python setuptools package is what we'll use to automate the rest of the
installation of Python packages.

If you're using a package manager to handle your Python installation, you can
use your package manager to install setuptools (0.6c9 or higher), like so:

.. sourcecode:: bash

   # For example, on Ubuntu 10.04:
   sudo apt-get install python-setuptools

   # Or on Mac OS X (with MacPorts):
   sudo port -v install py27-setuptools

   # Or on CentOS/RHEL/Fedora:
   sudo yum install python-setuptools

Otherwise, in the main MediaCore CE package directory, there is an install script
to get setuptools for you.

.. sourcecode:: bash

   # Run the setuptools install script in your MediaCore CE directory:
   sudo python ez_setup.py


Step 3: Installing Virtualenv
-----------------------------

First, check if you have virtualenv installed:

.. sourcecode:: bash

   # Check if you have virtualenv installed:
   python -c 'import virtualenv'

If you get no error, you can skip the rest of this step; virtualenv is already
installed!

If you get an error like the following, you'll need to install virtualenv:

.. sourcecode:: text

   Traceback (most recent call last):
     File "<string>", line 1, in <module>
   ImportError: No module named virtualenv

If you're using a package manager to handle your Python installation, you can
use your package manager to install virtualenv, like so:

.. sourcecode:: bash

   # For example, on Ubuntu 10.04:
   sudo apt-get install python-virtualenv

   # Or on Mac OS X (with MacPorts):
   # NOTE: While other options will install a script named simply 'virtualenv',
   #       macports will install a script named 'virtualenv-2.7'.
   #       If you install this way, remember to use 'virtualenv-2.7' instead of
   #       'virtualenv' in any commands below.
   sudo port -v install py27-virtualenv

   # Or on CentOS/RHEL/Fedora:
   sudo yum install python-virtualenv

Otherwise, you can get setuptools to automatically install virtualenv for you:

.. sourcecode:: bash

   # Install virtualenv via setuptools:
   sudo easy_install virtualenv
