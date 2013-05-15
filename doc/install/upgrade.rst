.. _install_upgrade:

======================
Upgrading MediaCore CE
======================

Upgrading MediaCore CE is relatively straightforward:

1. Rename the old virtualenv directory (previously called `mediacore_env`) and 
   create a new virtualenv.
2. Download and unpack the new version of MediaCore CE (or fetch from github 
   and checkout a new tag in git if you used the git deployment).
3. If you previously kept your data folder and the config file
   (e.g. `deployment.ini`) inside the MediaCore CE source code directory (as
   recommended in the docs before version 0.10) move them right next to the
   actual source code directory.
4. Update your configuration
5. Upgrade your database (completely automated)
6. Check your deployment scripts and post-upgrade cleanup

**NOTE 1:** We only support upgrades from version 0.9.0 and newer (any release 
after March 2011). If you are running an ancient version such as 0.8 please 
upgrade to 0.9.0 first (follow the upgrade steps in the 0.9 docs).

**NOTE 2:** `yourconf.ini` below should be replaced to refer to `development.ini`
or `deployment.ini`, depending on which one you have set up for your current
MediaCore CE installation.

**NOTE 3:** `/path/to/venv` and `/path/to/mediacore-old` below
should be replaced with the paths to your MediaCore CE Virtual Environment
directory and Installation directory, respectively.

**NOTE 4:** `mediacore-old` and `mediacore-new` below should be replaced with
the correct versions for your installation. For example, with `MediaCore-0.9.4`
and `MediaCore-0.10.0`, respectively.

**NOTE 5:** If you're a developer type, and you're tracking the latest changes
using git, you'll want to run `paster setup-app development.ini` after fetching
any new changes. This will ensure that your custom appearance css and your
Players table are up to date.

Step 1: Re-Create your Virtual Environment
------------------------------------------

If you perform only a minor upgrade (e.g. MediaCore CE 0.10.0 to 0.10.1) you 
can usually skip this step as we try not to change the database in a minor 
release.

.. sourcecode:: bash

   # Erase the old virtual environment:
   cd /path/to/venv
   cd ..
   mv venv venv.old

   # Create a new virtual environment:
   virtualenv --no-site-packages venv

   # Now, activate that virtual environment
   source venv/bin/activate

**NOTE 1:** Before MediaCore 0.10 the virtualenv folder was named 
'mediacore_env' in the documentation.

**NOTE 2:** If you kept your virtualenv inside the MediaCore CE source code 
directory (as recommended in the docs before version 0.10) please create the 
new virtualenv next to (not inside) the source code folder (run ``cd ..`` 
before creating the new virtualenv).


Step 2: Install the new MediaCore CE Files
------------------------------------------

`Download the latest official release of MediaCore CE <http://mediacorecommunity.org/download>`_ 
from our site, then unpack it beside your current MediaCore CE installation.

.. sourcecode:: bash

   # Download the latest distribution beside the current installation
   cd /path/to/mediacore-old/..
   wget http://mediacorecommunity.org/releases/mediacore-new.tar.gz

   # Unpack the downloaded distribution
   tar xzvf mediacore-new.tar.gz

   # You should now have a mediacore-old directory and mediacore-new directory
   # inside your current directory. Check that this is the case:
   ls

   # Install MediaCore and its dependencies into the new virtual environment
   cd mediacore-new
   python setup.py develop


Step 3: Migrate your Data (Media, Thumbnails)
-----------------------------------------------

Depending on the version you are upgrading from, this step is a little different:

a. If you your data directory is not inside your MediaCore CE source folder
   (recommended since MediaCore 0.10) you can skip this step.

b. If are upgrading from MediaCore CE **0.9.0 or newer**, you'll need to
   your data directory to a new place. It is recommended that you move the 
   directory and your config file (``yourconfig.ini``) right next (but not 
   inside) to your ``mediacore-new`` directory.

   .. sourcecode:: bash

      # Navigate to the parent directory, where mediacore-old and mediacore-new
      # both reside.
      cd /path/to/mediacore-old
      cd ..

      # Move over the old files (please note that there is no '/' after 'data')
      mv ./mediacore-old/data .
      mv ./mediacore-old/production.ini .


Step 4: Update your configuration
---------------------------------

If you perform only a minor upgrade (e.g. MediaCore CE 0.10.0 to 0.10.1) you 
can skip this step.

For major upgrades it is a good idea to create a new `deployment.ini` to check
for new configuration settings.

.. sourcecode:: bash

    cp yourconf.ini yourconf-old.ini
    paster make-config MediaCore deployment.ini

Copying over any modifications you made to the old one. At the very least, 
this means you should be copying over the database configuration (a line that 
looks something like):

.. sourcecode:: ini

   sqlalchemy.url = mysql://mediacore_user:mysecretpassword@localhost/mediacore?charset=utf8&use_unicode=0


Step 5: Upgrade your database
-----------------------------

Upgrading the database is a simple and straightforward step:

   .. sourcecode:: bash

      # Run the setup/upgrade script to upgrade your database.
      cd /path/to/mediacore-new
      paster setup-app yourconf.ini


Step 6: Check your deployment scripts and post-upgrade cleanup
--------------------------------------------------------------

If you already had MediaCore CE deployed using mod_wsgi (:ref:`install_apache-wsgi`)
or mod_fastcgi (:ref:`install_apache-fastcgi`), you'll want to re-deploy using
the new installation. In particular, take note of changes to the deployment
configurations (e.g. Apache configuration), changed deployment scripts 
(e.g. `mediacore.wsgi`, `mediacore.fcgi`) and required file permissions.

If you didn't separate source code and data in your previous version of 
MediaCore CE, you will need to adapt also the paths in your `mediacore.wsgi`
script (if you are using mod_wsgi).

If you recreated a new virtualenv in step 1 you also have to re-install any
plugins you have installed earlier.

When everything works fine your can also remove all the old directories 
`mediacore-old` and `venv-old`).

post-upgrade cleanup for MediaCore CE 0.10
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you're upgrading from MediaCore **0.9.x or smaller** and you use 
**Facebook comments** you have to run a special script to keep your existing
Facebook comments. Please read the release notes for more details.

.. sourcecode:: bash

      cd /path/to/mediacore-new
      python batch-scripts/upgrade/upgrade_from_v09_preserve_facebook_xid_comments.py \
        --app-secret=<your-app-secret> yourconfig.ini


Done!
-----

Your migration to the latest MediaCore CE is now complete.
