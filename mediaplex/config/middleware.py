"""TurboGears middleware initialization"""
from mediaplex.config.app_cfg import base_config
from mediaplex.config.environment import load_environment

#Use base_config to setup the necessary WSGI App factory. 
#make_base_app will wrap the TG2 app with all the middleware it needs. 
make_base_app = base_config.setup_tg_wsgi_app(load_environment)

def make_app(global_conf, full_stack=True, **app_conf):
    app = make_base_app(global_conf, full_stack=True, **app_conf)
    #Wrap your base turbogears app with custom middleware
    return app


