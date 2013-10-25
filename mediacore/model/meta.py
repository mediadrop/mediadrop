# This file is a part of MediaDrop (http://www.mediadrop.net),
# Copyright 2009-2013 MediaDrop contributors
# For the exact contribution history, see the git revision log.
# The source code contained in this file is licensed under the GPLv3 or
# (at your option) any later version.
# See LICENSE.txt in the main project directory, for more information.

"""SQLAlchemy Metadata and Session object"""
from sqlalchemy import MetaData
from sqlalchemy.orm import scoped_session, sessionmaker

__all__ = [
    'DBSession',
    'metadata',
]

# SQLAlchemy session manager. Updated by model.init_model()
# DBSession() returns the session object appropriate for the current request.
maker = sessionmaker()
DBSession = scoped_session(maker)

metadata = MetaData()
