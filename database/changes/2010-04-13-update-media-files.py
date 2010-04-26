from urlparse import urlparse
import os.path
import transaction

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

type_map = {
    'mp3': 'audio',
    'm4a': 'audio',
    'flac': 'audio',
}
embeddable_types = ['youtube', 'vimeo', 'google']

for f in DBSession.query(MediaFile):
    f.type = type_map.get(f.container, 'video')

    if f.container in embeddable_types:
        f.display_name = f.container.capitalize() + ' ID: ' + f.url
        f.embed = f.url
        f.url = None
        DBSession.add(f)
        continue

    url = urlparse(f.url)
    if url[1]:
        f.display_name = os.path.basename(url[2])
        DBSession.add(f)
        continue

    f.display_name = f.url
    f.file_name = f.url
    f.url = None
    DBSession.add(f)

commit_session()
