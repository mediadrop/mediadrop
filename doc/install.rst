.. _install:

============
Installation
============

Virtual Environments
--------------------

It's highly recommended that you create a virtual environment for your
Simpleplex installation, and any other Python apps you might use in the
future. Part of the power of Python is the wealth of libraries for developers
to take advantage of, but when dependencies conflict it can cause some serious
headaches. Save yourself loads of trouble later and use ``virtualenv``.

Let's create a new virtualenv for Simpleplex:

.. sourcecode:: bash

    $ virtualenv --no-site-packages simpleplex_env
    New python executable in simpleplex_env/bin/python
    Installing setuptools............done.

    $ cd simpleplex_env

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


Installing Simpleplex
---------------------

Finally we're ready to install Simpleplex and the few additional dependencies it
needs.

.. sourcecode:: bash

    $ git clone ssh://git@somerepo.com/simpleplex.git
    $ cd simpleplex
    $ python setup.py develop

Finally, create a MySQL database and run the setup.sql script. This can be done
in a number of ways, but here's how from the command line (assuming you've
already created an empty database).

.. sourcecode:: bash

    # Assuming your database is named simpleplex
    $ mysql5 -u root -p simpleplex < database/setup.sql

