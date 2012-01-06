.. _install_upgrade:

======================
Upgrading MediaCore CE
======================

Upgrading MediaCore CE is now relatively straightforward:

1. Make a new Virtual Environment
2. Download and unpack the new version of MediaCore CE
3. Move all your old media files and thumbnails into the new MediaCore CE
   directory
4. Set up your .ini config files in the new MediaCore CE directory
5. Upgrade your database (now completely automated!)

**NOTE 1:** `yourconf.ini` below should be replaced to refer to `development.ini`
or `deployment.ini`, depending on which one you have set up for your current
MediaCore CE installation.

**NOTE 2:** `/path/to/mediacore_env` and `/path/to/MediaCore-OLD` below
should be replaced with the paths to your MediaCore CE Virtual Environment
directory and Installation directory, respectively.

**NOTE 3:** `MediaCore-OLD` and `MediaCore-NEW` below should be replaced with
the correct versions for your installation. For example, with `MediaCore-0.8.2`
and `MediaCore-0.9.0`, respectively.

**NOTE 4:** If you're a developer type, and you're tracking the latest changes
using git, you'll want to run `paster setup-app development.ini` after fetching
any new changes. This will ensure that your custom appearance css and your
Players table are up to date.


Step 1: Re-Create Your Virtual Environment
------------------------------------------

.. sourcecode:: bash

   # Erase the old virtual environment:
   cd /path/to/mediacore_env
   cd ..
   rm -rf mediacore_env

   # Create a new virtual environment:
   virtualenv --no-site-packages mediacore_env

   # Now, activate that virtual environment
   source mediacore_env/bin/activate

Step 2: Install The New MediaCore CE Files
------------------------------------------
`Download the latest official release of MediaCore CE
<http://getmediacore.com/download>`_ from our site, then unpack it beside
your current MediaCore CE installation.

.. sourcecode:: bash

   # Download the latest distribution beside the current installation
   cd /path/to/MediaCore-OLD
   cd ..
   wget http://getmediacore.com/files/MediaCore-NEW.tar.gz

   # Unpack the downloaded distribution
   tar xzvf MediaCore-NEW.tar.gz

   # You should now have a MediaCore-OLD directory and MediaCore-NEW directory
   # inside your current directory. Check that this is the case:
   ls

   # Install MediaCore and its dependencies into the new virtual environment
   cd MediaCore-NEW
   python setup.py develop


Step 3: Migrate Your Media Files and Thumbnails
-----------------------------------------------

Depending on the version you are upgrading from, this step is a little different:

a. If you are upgrading from MediaCore CE **0.8.2 or older**, you'll need to
   move all of the relevant files in ``./data/`` and
   ``./mediacore/public/images/podcasts/`` and
   ``./mediacore/public/images/media/`` from your old installation directory
   to your new installation directory.

   .. sourcecode:: bash

      # Navigate to the parent directory, where MediaCore-OLD and MediaCore-NEW
      # both reside.
      cd /path/to/MediaCore-OLD
      cd ..

      # Move over the old media files.
      mv ./MediaCore-OLD/data/deleted ./MediaCore-NEW/data/
      mv ./MediaCore-OLD/data/media ./MediaCore-NEW/data/

      # Move over the old thumbnails.
      mv ./MediaCore-OLD/mediacore/public/images/podcasts/[0-9]* ./MediaCore-NEW/data/images/podcasts/
      mv ./MediaCore-OLD/mediacore/public/images/media/[0-9]* ./MediaCore-NEW/data/images/media/


b. If you are upgrading from MediaCore CE **0.9.0 or newer**, you'll need to
   move all of the relevant files in ``./data`` from your old installation
   directory to your new installation directory.

   .. sourcecode:: bash

      # Navigate to the parent directory, where MediaCore-OLD and MediaCore-NEW
      # both reside.
      cd /path/to/MediaCore-OLD
      cd ..

      # Move over the old files
      mv ./MediaCore-OLD/data/media/* ./MediaCore-NEW/data/media/
      mv ./MediaCore-OLD/data/deleted/* ./MediaCore-NEW/data/deleted/
      mv ./MediaCore-OLD/data/appearance/* ./MediaCore-NEW/data/appearance/
      mv ./MediaCore-OLD/data/images/media/[0-9]* ./MediaCore-NEW/data/images/media/
      mv ./MediaCore-OLD/data/images/podcasts/[0-9]* ./MediaCore-NEW/data/images/podcasts/


Step 4: Create a New Config
---------------------------

Edit the new `development.ini` file, copying over any modifications you made to
the old one. At the very least, this means you should be copying over the line
that looks something like:

.. sourcecode:: ini

   sqlalchemy.url = mysql://mediacore_user:mysecretpassword@localhost/mediacore?charset=utf8&use_unicode=0

If you are running MediaCore CE via a deployment method described the installation
docs, this is the point where you will also want to re-create your
`deployment.ini` and update your WSGI or FastCGI script, replacing all
references to `/path/to/MediaCore-OLD` with `/path/to/MediaCore-NEW`.


Step 5: Upgrading Your Database
-------------------------------

This step is slightly different depending on which version you are upgrading
from. See the individual commands below:

a.  If you're upgrading from **0.7.2** (released January 2010):

   .. sourcecode:: bash

      # Run the upgrade script to upgrade your database.
      cd /path/to/MediaCore-NEW
      python batch-scripts/upgrade/upgrade-from-v072.py yourconf.ini


b.  Or, if you're upgrading from **0.8.0** (released May 2010):

   .. sourcecode:: bash

      # Run the upgrade script to upgrade your database.
      cd /path/to/MediaCore-NEW
      python batch-scripts/upgrade/upgrade-from-v080.py yourconf.ini


c.  Or, if you're upgrading from **0.8.2, 0.9.0, or newer** (released after August 2010):

   .. sourcecode:: bash

      # Run the setup/upgrade script to upgrade your database.
      cd /path/to/MediaCore-NEW
      paster setup-app yourconf.ini


Step 6: Update your Deployment Configuration
--------------------------------------------

If you already had MediaCore CE deployed using mod_wsgi (:ref:`install_apache-wsgi`)
or mod_fastcgi (:ref:`install_apache-fastcgi`), you'll want to re-deploy using
the new installation. In particular, take note of changes to the deployment
configurations and required file permissions.

Done!
-----

Your migration to the latest MediaCore CE is now complete.
