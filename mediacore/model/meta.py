"""SQLAlchemy Metadata and Session object"""
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker
from zope.sqlalchemy import ZopeTransactionExtension

__all__ = ['Base', 'DBSession']

# SQLAlchemy session manager. Updated by model.init_model()
# DBSession() returns the session object appropriate for the current request.
maker = sessionmaker(extension=ZopeTransactionExtension())
DBSession = scoped_session(maker)

# The declarative Base
Base = declarative_base()
