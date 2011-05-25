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
