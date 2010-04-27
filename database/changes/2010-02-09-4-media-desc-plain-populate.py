import os
import urllib2
import urllib
import transaction
import time
import sys

from mediacore.model import *
from sqlalchemy import create_engine, select
from sqlalchemy.orm import eagerload, undefer
from paste.deploy import appconfig
from pylons import config
from mediacore.config.environment import load_environment

conf = appconfig('config:development.ini', relative_to='../..')
load_environment(conf.global_conf, conf.local_conf)

from mediacore.lib.helpers import strip_xhtml, line_break_xhtml

def commit_session():
    DBSession.flush()
    transaction.commit()

for m in DBSession.query(Media):
    m.description_plain = strip_xhtml(line_break_xhtml(line_break_xhtml(m.description)), True)
    DBSession.add(m)

commit_session()
