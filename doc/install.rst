.. _install:

============
Installation
============

Virtual Environments
--------------------

It's highly recommended that you create a virtual environment for your
MediaCore installation, and any other Python apps you might use in the
future. Part of the power of Python is the wealth of libraries for developers
to take advantage of, but when dependencies conflict it can cause some serious
headaches. Save yourself loads of trouble later and use ``virtualenv``.

Let's create a new virtualenv for MediaCore:

.. sourcecode:: bash

    $ virtualenv --no-site-packages mediacore_env
    New python executable in mediacore_env/bin/python
    Installing setuptools............done.

    $ cd mediacore_env

The ``--no-site-packages`` command prevents this virtualenv from accessing any
of the libraries you've installed to the system site-packages folder, so none
of the packages you've installed to date will be accessible.

.. note::

    :For Macports on OS X Users:

    You'll have to manually copy the MySQL library files into your new
    virtualenv. Assuming default paths, this should work:

    .. sourcecode:: bash

        $ cp -r /opt/local/Library/Frameworks/Python.framework/Versions/2.5/lib/python2.5/site-packages/MySQL* \
             lib/python2.5/site-packages/
        $ cp /opt/local/Library/Frameworks/Python.framework/Versions/2.5/lib/python2.5/site-packages/_mysql* \
             lib/python2.5/site-packages/

    The Python Imaging Library (PIL) cannot be installed on Mac OS X with
    easy_install/setuptools. We recommend using the MacPorts distribution.

    .. sourcecode:: bash

       $ sudo port install py25-pil
       $ cp -r /opt/local/lib/python2.5/site-packages/PIL* \
               lib/python2.5/site-packages/


Once created you must **activate** it before proceeding with the installation.
Indeed, *any time* you work with the app on the command line, you must remember
to activate the virtualenv.

.. sourcecode:: bash

    $ source bin/activate


Installing TurboGears
---------------------

Assuming you're using a fresh ``virtualenv``, TurboGears won't be installed yet.
The recommended version can be installed with this command:

.. sourcecode:: bash

    $ easy_install -i http://www.turbogears.org/2.0/downloads/current/index tg.devtools


Installing MediaCore
---------------------

Finally we're ready to install MediaCore and the few additional dependencies it
needs.

.. sourcecode:: bash

    $ git clone ssh://git@somerepo.com/mediacore.git
    $ cd mediacore
    $ python setup.py develop

Finally, create a MySQL database and run the setup.sql script. This can be done
in a number of ways, but here's how from the command line (assuming you've
already created an empty database).

.. sourcecode:: bash

    # Assuming your database is named mediacore
    $ mysql5 -u root -p mediacore < database/setup.sql

Configuration
-------------

Each installation of MediaCore has its own config file, as with most Pylons
projects. Generate a new one with this command:

.. sourcecode:: bash

    $ paster make-config mediacore deployment.ini

.. note::

    ``paster`` basically copies ``mediacore/config/deployment.ini_tmpl`` to
    create the config. It also generates unique secret keys for cookie and auth
    encryption, which ensures there will be no security issues caused by default
    keys being used in production.

The INI config file is for only the most sensitive and important settings.
These are the settings that should only be set by someone who knows what they're
doing. More commonly edited settings, which won't break things if tampered with,
are located in the admin UI in the settings tab.

Creating Your Database
----------------------

Import database/init.sql

