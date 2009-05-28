from tg.configuration import AppConfig, Bunch, config
from routes import Mapper

import mediaplex
from mediaplex import model
from mediaplex.lib import app_globals, helpers

class MediaplexConfig(AppConfig):
    def setup_routes(self):
        """Setup our custom named routes"""
        map = Mapper(directory=config['pylons.paths']['controllers'],
                    always_scan=config['debug'])

        # home page redirect
        map.redirect('/', '/video-flow')

        # routes for all non-view, non-index, video actions
        map.connect('/video-{action}', controller='video', requirements=dict(action='flow|upload|upload_submit|upload_submit_async|upload_success'))
        map.connect('/video-{action}/{slug}', slug=None, controller='video', requirements=dict(action='tags|rate'))
        # route for viewing videos and other video related actions
        map.connect('/video/{slug}/{action}', controller='video', action='view')
        # admin routes
        map.connect('/admin/video', controller='videoadmin', action='index')
        map.connect('/admin/video/{id}/{action}', controller='videoadmin', action='edit')

        map.connect('/admin/comments', controller='commentadmin', action='index')
        map.connect('/admin/comments/{id}/{action}', controller='commentadmin', action='edit')

        # Set up the default route
        map.connect('/{controller}/{action}', action='index')

        # Set up a fallback route for object dispatch
        map.connect('*url', controller='root', action='routes_placeholder')

        config['routes.map'] = map


base_config = MediaplexConfig()
base_config.renderers = []

base_config.package = mediaplex

#Set the default renderer
base_config.default_renderer = 'genshi'
base_config.renderers.append('genshi')
# if you want raw speed and have installed chameleon.genshi
# you should try to use this renderer instead.
# warning: for the moment chameleon does not handle i18n translations
#base_config.renderers.append('chameleon_genshi')

#Configure the base SQLALchemy Setup
base_config.use_sqlalchemy = True
base_config.model = mediaplex.model
base_config.DBSession = mediaplex.model.DBSession

# Configure the authentication backend
base_config.auth_backend = 'sqlalchemy'
base_config.sa_auth.dbsession = model.DBSession
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
