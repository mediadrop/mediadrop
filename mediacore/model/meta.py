"""SQLAlchemy Metadata and Session object"""
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker

__all__ = ['Base', 'DBSession']

# SQLAlchemy session manager. Updated by model.init_model()
# DBSession() returns the session object appropriate for the current request.
DBSession = scoped_session(sessionmaker())

# The declarative Base
Base = declarative_base()
