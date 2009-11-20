from tg.configuration import AppConfig, Bunch, config

import mediacore
from mediacore import model
from mediacore.config import routing
from mediacore.lib import app_globals, helpers, auth


class MediaCoreConfig(AppConfig):
    def setup_routes(self):
        """Override the TG object dispatch with custom routes."""
        config['routes.map'] = routing.make_map()

    def setup_sa_auth_backend(self):
        """Extend the TG method which sets sa_auth to the config.

        Now it actually does something!!! Though setting the cookie_secret
        in a deploy.ini is officially "supported", apparently no one tested
        it because it clearly doesn't "work". In fact, the glorious work
        that :meth:`AppConfig.setup_sa_auth_backend` *normally* does goes
        completely to waste because :meth:`AppConfig.add_auth_middleware`
        gets its config values from :attr:`AppConfig.sa_auth` which are
        defined in :mod:`mediacore.config.app_cfg`. This hack will have to
        do for now, too much time has been wasted on this already.
        """
        super(MediaCoreConfig, self).setup_sa_auth_backend()
        if 'sa_auth.cookie_secret' in config:
            config['sa_auth']['cookie_secret'] = config['sa_auth.cookie_secret']
        self.sa_auth = config['sa_auth']


# Normal TG-style project configuration
base_config = MediaCoreConfig()
base_config.renderers = []

base_config.package = mediacore

#Set the default renderer
base_config.default_renderer = 'genshi'
base_config.renderers.append('genshi')
# if you want raw speed and have installed chameleon.genshi
# you should try to use this renderer instead.
# warning: for the moment chameleon does not handle i18n translations
#base_config.renderers.append('chameleon_genshi')

#Configure the base SQLALchemy Setup
base_config.use_sqlalchemy = True
base_config.model = mediacore.model
base_config.DBSession = mediacore.model.DBSession

# Configure the authentication backend
base_config.auth_backend = 'sqlalchemy'
base_config.sa_auth.dbsession = model.DBSession

# The salt used to encrypt auth cookie data. This value must be unique to
# each deployment so it comes from the INI config file and is randomly
# generated when you run paster make-config
# base_config.sa_auth.cookie_secret = 'mysecretcookie'
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

# Hook into the auth process to read the session ID out of the POST vars
# during flash upload requests.
base_config.sa_auth.classifier = auth.classifier_for_flash_uploads


# Mimetypes
base_config.mimetype_lookup = {
    # TODO: Replace this with a more complete list.
    #       or modify code to detect mimetype from something other than ext.
    '.m4a':  'audio/mpeg',
    '.m4v':  'video/mpeg',
    '.mp3':  'audio/mpeg',
    '.mp4':  'audio/mpeg',
    '.flac': 'audio/flac',
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

base_config.album_art_sizes = { # the dimensions (in pixels) to scale album art
    'ss':(128,  72),
    's': (162,  91),
    'm': (240, 135),
    'l': (410, 231),
}

