"""Setup the MediaCore application"""
import logging

import pylons
import transaction

from mediacore.config.environment import load_environment
from mediacore.model import DBSession, metadata

log = logging.getLogger(__name__)

def setup_app(command, conf, vars):
    """Place any commands to setup mediacore here"""
    # Don't reload the app if it was loaded under the testing environment
    if not pylons.test.pylonsapp:
        load_environment(conf.global_conf, conf.local_conf)

    # Load the models
    print "Creating tables"
    metadata.create_all(bind=DBSession.bind)

    # Set up any useful initial data here.
    # TODO: Use this file to replace setup.sql
    DBSession.flush()
    transaction.commit()
    print "Successfully setup"
