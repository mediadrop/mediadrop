"""Setup the MediaCore application"""
import logging

import transaction
from pylons import config

from mediacore.config.environment import load_environment

log = logging.getLogger(__name__)

def setup_app(command, conf, vars):
    """Place any commands to setup mediacore here"""
    # Don't reload the app if it was loaded under the testing environment
    if not pylons.test.pylonsapp:
        load_environment(conf.global_conf, conf.local_conf)

    # Load the models
    from mediacore import model
    print "Creating tables"
    model.metadata.create_all(bind=config['pylons.app_globals'].sa_engine)

    # Set up any useful initial data here.
    # TODO: Use this file to replace setup.sql

    model.DBSession.flush()
    transaction.commit()
    print "Successfully setup"
