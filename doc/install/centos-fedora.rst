:orphan:

RHEL/CentOS and Fedora
----------------------------------------------

RHEL (+ clones like CentOS) is the preferred platform for running MediaDrop
because of its long-term support and high-quality packages.

MediaDrop runs on RHEL 5 and 6 as well as any support version of Fedora.

MySQL server
""""""""""""""""""""""""""""""""""""""""

If you don't have a working MySQL server ready you should install the required
packages:

.. sourcecode:: bash

    yum install mysql mysql-server

Please note that you need to secure your install, grant a MySQL user with 
sufficient privileges and create a new database for MediaDrop. However these
procedures are out of scope for this documentation.

System libraries and development headers
""""""""""""""""""""""""""""""""""""""""

.. sourcecode:: bash

    yum install gcc libjpeg-devel zlib-devel freetype-devel python-devel mysql-devel

Python libraries and tools
""""""""""""""""""""""""""""""""""""""""

.. sourcecode:: bash

    yum install python-setuptools

`virtualenv <pypi.python.ort/pypi/virtualenv>`_ is not part of RHEL's standard 
package set. You can either install install it manually (see the 'Installation'
section on `virtualenv's pypi page <https://pypi.python.org/pypi/virtualenv>`_) or
enable the `Fedora EPEL <http://fedoraproject.org/wiki/EPEL>`_ and install the 
``python-virtualenv`` package.

On Fedora you can just install virtualenv using yum:

.. sourcecode:: bash

    # RHEL with Fedora EPEL enabled or plain Fedora!
    yum install python-virtualenv


RHEL/CentOS 5 and Python 2.4
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Please note that you need virtualenv < 1.8 if you plan to use Python 2.4 (RHEL 5).

RHEL 5.x comes with Python 2.4. While MediaDrop 0.10 still works with 
Python 2.4 support for that old version of Python (released initially in 
November 2004) will be dropped eventually. Also some plugins might not work 
with 2.4.

The recommend setup on RHEL 5 is to install Python 2.6 through 
`Fedora EPEL <http://fedoraproject.org/wiki/EPEL>`_. The EPEL Python package 
does not replace the RHEL-provided Python 2.4 and therefore won't affect the
rest of the system.

After you enabled Fedora EPEL you can install the required Python 2.6 packages:

.. sourcecode:: bash

    yum install python26 python26-devel python26-setuptools python26-virtualenv

Also later in the install docs you must use ``python26`` wherever the docs say
``python``. Also ``virtualenv`` must be replaced by ``virtualenv-2.6``. And last
but not least you need to install the ``python26-mod_wsgi`` for production
deployments.
