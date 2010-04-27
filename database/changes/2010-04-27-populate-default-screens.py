from urlparse import urlparse
import os.path
import transaction

from mediacore.model import *
from sqlalchemy import create_engine, select
from sqlalchemy.orm import eagerload, undefer
from paste.deploy import appconfig
from pylons import config
from mediacore.config.environment import load_environment
from mediacore.lib import helpers

conf = appconfig('config:local.ini', relative_to='../..')
load_environment(conf.global_conf, conf.local_conf)

helpers.config = conf
helpers.config['thumb_sizes'] = { # the dimensions (in pixels) to scale thumbnails
    'media': {
        's': (128,  72),
        'm': (160,  90),
        'l': (560, 315),
    },
    'podcasts': {
        's': (128, 128),
        'm': (160, 160),
        'l': (600, 600),
    },
}

for collection in (Media.query, Podcast.query):
    for item in collection:
        if not helpers.thumb_path(item, 'm', exists=True):
            helpers.create_default_thumbs_for(item)
            print 'Default thumbs created for', item
