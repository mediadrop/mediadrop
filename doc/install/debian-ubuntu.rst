:orphan:

Debian and Ubuntu
----------------------------------------------

The following instructions were tested using Debian 6 ("Squeeze") and Ubuntu 12.04 LTS ("Precise Pangolin"). Very likely other Debian/Ubuntu versions work exactly the same.

In the following section we use 'apt-get' to install system packages. If you previously used 'aptitude' please replace 'apt-get' with 'aptitude'.

MySQL server
""""""""""""""""""""""""""""""""""""""""

If you don't have a working MySQL server ready you should install the required
packages:

.. sourcecode:: bash

    sudo apt-get install mysql-server mysql-client 

Please note that you need to secure your install, grant a MySQL user with 
sufficient privileges and create a new database for MediaDrop. However these
procedures are out of scope for this documentation.


System libraries and development headers
""""""""""""""""""""""""""""""""""""""""

.. sourcecode:: bash

    sudo apt-get install libjpeg-dev zlib1g-dev libfreetype6-dev libmysqlclient-dev python-dev
    
Python libraries and tools
""""""""""""""""""""""""""""""""""""""""

.. sourcecode:: bash

    sudo apt-get install python-setuptools python-virtualenv

