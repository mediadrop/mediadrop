# This file is a part of MediaDrop (http://www.mediadrop.net),
# Copyright 2009-2013 MediaCore Inc., Felix Schwarz and other contributors.
# For the exact contribution history, see the git revision log.
# The source code contained in this file is licensed under the GPLv3 or
# (at your option) any later version.
# See LICENSE.txt in the main project directory, for more information.

"""
This is the database migration repository for MediaCore.

To initialize the database and/or apply pending migrations,
run websetup.py with this command:

     ``paster setup-app yourconf.ini``

NOTE: If you are upgrading from MediaCore 0.7.2 or 0.8.0, you must first
      run the script for your version, to initialize migrations for the
      version of the schema you're using:

          0.7.2: ``batch-scripts/upgrade/upgrade-from-v072.py yourconf.ini``
          0.8.0: ``batch-scripts/upgrade/upgrade-from-v080.py yourconf.ini``


More information at
http://code.google.com/p/sqlalchemy-migrate/
"""