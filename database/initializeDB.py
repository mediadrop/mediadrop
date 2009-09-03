"""
Script for creating database tables.
Will be expanded to include dummy data.

IMPORTANT! Configure MySQL to use the InnoDB table engine by default.
           Otherwise foreign key constraints will not be added.
"""

from simpleplex.model import DBSession, Video, metadata
from sqlalchemy import create_engine
import transaction

# Prepare the database connection
engine = create_engine('mysql://root:happyplanet@localhost/simpleplex', echo=True)
DBSession.configure(bind=engine)

# Create the tables
metadata.drop_all(engine)
metadata.create_all(engine)


# Save the page object to the in memory DBSession
transaction.commit()
