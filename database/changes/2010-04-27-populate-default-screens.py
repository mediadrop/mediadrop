from mediacore.model import *
from paste.deploy import appconfig
from pylons import config
from mediacore.config.environment import load_environment
from mediacore.lib import helpers
from mediacore.lib.thumbnails import thumb_path, create_default_thumbs_for

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
        if not thumb_path(item, 'm', exists=True):
            create_default_thumbs_for(item)
            print 'Default thumbs created for', item
