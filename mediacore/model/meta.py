# This file is a part of MediaCore CE, Copyright 2009-2012 MediaCore Inc.
# The source code contained in this file is licensed under the GPL.
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
