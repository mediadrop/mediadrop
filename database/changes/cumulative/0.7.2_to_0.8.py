import os.path
import transaction

from mediacore.config.environment import load_environment
from paste.deploy import appconfig
from pylons import config
from urlparse import urlparse

conf = appconfig('config:deployment.ini', relative_to='../../..')
load_environment(conf.global_conf, conf.local_conf)

from mediacore.lib import helpers
from mediacore.model import *
from mediacore.model.meta import DBSession

def commit_session():
    DBSession.flush()
    transaction.commit()

for m in DBSession.query(Media):
    p = helpers.line_break_xhtml(m.description)
    p = helpers.line_break_xhtml(p)
    p = helpers.strip_xhtml(p, True)
    m.description_plain = p
    DBSession.add(m)

for m in DBSession.query(Media):
    m.update_popularity()
    DBSession.add(m)

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

