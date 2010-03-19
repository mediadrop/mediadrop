import transaction
import pkg_resources
pkg_resources.require('TurboGears2')

from mediacore.model import *
from sqlalchemy import create_engine, select
from sqlalchemy.orm import eagerload, undefer
from paste.deploy import appconfig
from pylons import config
from mediacore.config.environment import load_environment

conf = appconfig('config:deployment.ini', relative_to='../..')
load_environment(conf.global_conf, conf.local_conf)

def commit_session():
    DBSession.flush()
    transaction.commit()

for m in DBSession.query(Media):
    m.update_rating()
    DBSession.add(m)

commit_session()
