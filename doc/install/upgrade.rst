.. _install_upgrade:

===================
Upgrading MediaCore
===================

Upgrading MediaCore is now relatively straightforward:

1. Make a new Virtual Environment
2. Download and unpack the new version of MediaCore
3. Move all your old media files and thumbnails into the new MediaCore
   directory
4. Set up your .ini config files in the new MediaCore directory
5. Upgrade your database (now completely automated!)

**NOTE 1:** `yourconf.ini` below should be replaced to refer to `development.ini`
or `deployment.ini`, depending on which one you have set up for your current
MediaCore installation.

**NOTE 2:** `/path/to/mediacore_env` and `/path/to/MediaCore-OLD` below
should be replaced with the paths to your MediaCore Virtual Environment
directory and Installation directory, respectively.

**NOTE 3:** `MediaCore-OLD` and `MediaCore-NEW` below should be replaced with
the correct versions for your installation. For example, with `MediaCore-0.8.0`
and `MediaCore-0.8.2`, respectively.


Step 1: Re-Create Your Virtual Environment
------------------------------------------

.. sourcecode:: bash

   # Erase the old virtual environment:
   cd /path/to/mediacore_env
   cd ..
   rm -rf mediacore_env

   # Create a new virtual environment:
   virtualenv-2.5 --no-site-packages mediacore_env

   # Now, activate that virtual environment
   source mediacore_env/bin/activate

Step 2: Install The New MediaCore Files
---------------------------------------
`Download the latest official release of Mediacore
<http://getmediacore.com/download>`_ from our site, then unpack it beside
your current MediaCore installation.

.. sourcecode:: bash

   # Download the latest distribution beside the current installation
   cd /path/to/MediaCore-OLD
   cd ..
   wget http://getmediacore.com/files/MediaCore-NEW.tar.gz

   # Unpack the downloaded distribution
   tar xzvf MediaCore-NEW.tar.gz

   # Install MediaCore and its dependencies into the new virtual environment
   cd MediaCore-NEW
   python2.5 setup.py develop


Step 3: Migrate Your Media Files and Thumbnails
-----------------------------------------------

Here we will move all of the relevant files in ``./data/``
and ``./mediacore/public/images/podcasts/``
and ``./mediacore/public/images/media/`` from your old installation directory
to your new installation directory.

.. sourcecode:: bash

   # Navigate to the parent directory, where MediaCore-OLD and MediaCore-NEW
   # both reside.
   cd /path/to/MediaCore-OLD
   cd ..

   # Move over the old media files.
   mv ./MediaCore-OLD/data/deleted ./MediaCore-NEW/data/
   mv ./MediaCore-OLD/data/media ./MediaCore-NEW/data/

   # Ensure that the new default thumbnails are saved.
   cp ./MediaCore-NEW/mediacore/public/images/podcasts/* ./MediaCore-OLD/mediacore/public/images/podcasts/
   cp ./MediaCore-NEW/mediacore/public/images/media/* ./MediaCore-OLD/mediacore/public/images/media/

   # Move over the old thumbnails.
   mv ./MediaCore-OLD/mediacore/public/images/podcasts ./MediaCore-NEW/mediacore/public/images/
   mv ./MediaCore-OLD/mediacore/public/images/media ./MediaCore-NEW/mediacore/public/images/


Step 4: Create a New Config
---------------------------

Edit the new `development.ini` file, copying over any modifications you made to
the old one. At the very least, this means you should be copying over the line
that looks something like:

.. sourcecode:: ini

   sqlalchemy.url = mysql://mediacore_user:mysecretpassword@localhost/mediacore?charset=utf8&use_unicode=0

If you are running MediaCore via a deployment method described the installation
docs, this is the point where you will also want to re-create your
`deployment.ini` and update your WSGI or FastCGI script, replacing all
references to `/path/to/MediaCore-OLD` with `/path/to/MediaCore-NEW`.


Step 5: Upgrading Your Database
-------------------------------

This step is slightly different depending on which version you are upgrading
from. See the individual commands below:

Step 5.0: Upgrade Database from MediaCore 0.7.2
-----------------------------------------------

.. sourcecode:: bash

   # Run the upgrade script to upgrade your database.
   cd /path/to/MediaCore-NEW
   python batch-scripts/upgrade/upgrade-from-v072.py yourconf.ini


Step 5.1: Upgrade Database from MediaCore 0.8.0
-----------------------------------------------

.. sourcecode:: bash

   # Run the upgrade script to upgrade your database.
   cd /path/to/MediaCore-NEW
   python batch-scripts/upgrade/upgrade-from-v080.py yourconf.ini


Step 5.2: Upgrade Database from MediaCore >= 0.8.2
--------------------------------------------------

.. sourcecode:: bash

   # Run the setup/upgrade script to upgrade your database.
   cd /path/to/MediaCore-NEW
   paster setup-app yourconf.ini

Done!
-----

Your migration to the latest MediaCore is now complete.
