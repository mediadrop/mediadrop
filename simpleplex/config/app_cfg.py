from tg.configuration import AppConfig, Bunch, config

import simpleplex
from simpleplex import model
from simpleplex.config.routing import make_map
from simpleplex.lib import app_globals, helpers, auth

# Routes are defined separately, and we must override the very basic default
# TG route setup prior to its instantiation.
class SimpleplexConfig(AppConfig):
    """:class:`tg.configuration.AppConfig` extension for :mod:`routes` usage"""
    def setup_routes(self):
        config['routes.map'] = make_map()

# Normal TG-style project configuration
base_config = SimpleplexConfig()
base_config.renderers = []

base_config.package = simpleplex

#Set the default renderer
base_config.default_renderer = 'genshi'
base_config.renderers.append('genshi')
# if you want raw speed and have installed chameleon.genshi
# you should try to use this renderer instead.
# warning: for the moment chameleon does not handle i18n translations
#base_config.renderers.append('chameleon_genshi')

#Configure the base SQLALchemy Setup
base_config.use_sqlalchemy = True
base_config.model = simpleplex.model
base_config.DBSession = simpleplex.model.DBSession

# Configure the authentication backend
base_config.auth_backend = 'sqlalchemy'
base_config.sa_auth.dbsession = model.DBSession
base_config.sa_auth.cookie_secret = 'mysecretcookie' # TODO: customize this
# what is the class you want to use to search for users in the database
base_config.sa_auth.user_class = model.User
# what is the class you want to use to search for groups in the database
base_config.sa_auth.group_class = model.Group
# what is the class you want to use to search for permissions in the database
base_config.sa_auth.permission_class = model.Permission

# override this if you would like to provide a different who plugin for
# managing login and logout of your application
base_config.sa_auth.form_plugin = None

# You may optionally define a page where you want users to be redirected to
# on login:
base_config.sa_auth.post_login_url = '/post_login'

# You may optionally define a page where you want users to be redirected to
# on logout:
base_config.sa_auth.post_logout_url = '/post_logout'

# custom auth goodness
base_config.sa_auth.classifier = auth.classifier_for_flash_uploads


# Mimetypes
base_config.mimetype_lookup = {
    # TODO: Replace this with a more complete list.
    #       or modify code to detect mimetype from something other than ext.
    '.m4a':  'audio/mpeg',
    '.m4v':  'video/mpeg',
    '.mp3':  'audio/mpeg',
    '.mp4':  'audio/mpeg',
    '.3gp':  'video/3gpp',
    '.3g2':  'video/3gpp',
    '.divx': 'video/divx', # I don't think this is registered with the IANA
    '.dv':   'video/x-dv',
    '.dvx':  'video/divx', # Oh well, divx is just a proprietary mpeg-4 encoder
    '.flv':  'video/x-flv', # made up, it's what everyone uses anyway.
    '.mov':  'video/quicktime',
    '.mpeg': 'video/mpeg',
    '.mpg':  'video/mpeg',
    '.qt':   'video/quicktime',
    '.vob':  'video/x-vob', # multiplexed container format
    '.wmv':  'video/x-ms-wmv',
}

base_config.embeddable_filetypes = {
    'youtube': {
        'play': 'http://youtube.com/v/%s',
        'link': 'http://youtube.com/watch?v=%s',
        'pattern': '^(http(s?)://)?(www.)?youtube.com/watch\?(.*&)?v=(?P<id>[^&#]+)'
    },
    'google': {
        'play': 'http://video.google.com/googleplayer.swf?docid=%s&hl=en&fs=true',
        'link': 'http://video.google.com/videoplay?docid=%s',
        'pattern': '^(http(s?)://)?video.google.com/videoplay\?(.*&)?docid=(?P<id>-\d+)'
    },
    'vimeo': {
        'play': 'http://vimeo.com/moogaloop.swf?clip_id=%d&server=vimeo.com&show_title=1&show_byline=1&show_portrait=0&color=&fullscreen=1',
        'link': 'http://vimeo.com/%s',
        'pattern': '^(http(s?)://)?(www.)?vimeo.com/(?P<id>\d+)'
    },
}

base_config.playable_types = {
    'audio': ('mp3', 'mp4', 'm4a'),
    'video': ('flv', ),
    None: (),
}

# Email Notification Config
base_config.media_notifications = True
base_config.comment_notifications = True
base_config.media_notification_addresses = [
    'anthony@simplestation.com',
    'videos@tmcyouth.com',
]
base_config.comment_notification_addresses = [
    'anthony@simplestation.com',
    'notifications@tmcyouth.com',
]
base_config.support_addresses = [
    'webteam@tmcyouth.com',
    'anthony@simplestation.com',
]
base_config.notification_from_address = 'noreply@tmcyouth.com'

# If ftp_storage is enabled, then media_dir is not used for storing
# uploaded media files, and they are instead uploaded to the FTP server.
base_config.ftp_storage = False
base_config.ftp_upload_integrity_retries = 10

base_config.max_upload_size = 2 * 1024 * 1024 * 1024 # 2 Gigabytes (binary)

base_config.album_art_sizes = { # the dimensions (in pixels) to scale album art
    'ss':(128,  72),
    's': (162,  91),
    'm': (240, 135),
    'l': (410, 231),
}

