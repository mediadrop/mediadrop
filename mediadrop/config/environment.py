# This file is a part of MediaDrop (http://www.mediadrop.net),
# Copyright 2009-2013 MediaDrop contributors
# For the exact contribution history, see the git revision log.
# The source code contained in this file is licensed under the GPLv3 or
# (at your option) any later version.
# See LICENSE.txt in the main project directory, for more information.
"""Pylons environment configuration"""

import os

from formencode.api import get_localedir as get_formencode_localedir
from genshi.filters.i18n import Translator
import pylons
from pylons import translator
from pylons.configuration import PylonsConfig
from sqlalchemy import engine_from_config

import mediadrop.lib.app_globals as app_globals
import mediadrop.lib.helpers

from mediadrop.config.routing import create_mapper, add_routes
from mediadrop.lib.templating import TemplateLoader
from mediadrop.model import Media, Podcast, init_model
from mediadrop.plugin import PluginManager, events

def load_environment(global_conf, app_conf):
    """Configure the Pylons environment via the ``pylons.config`` object"""
    config = PylonsConfig()

    # Pylons paths
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    paths = dict(root=root,
                 controllers=os.path.join(root, 'controllers'),
                 static_files=os.path.join(root, 'public'),
                 templates=[os.path.join(root, 'templates')])

    # Initialize config with the basic options
    config.init_app(global_conf, app_conf, package='mediadrop', paths=paths)

    # Initialize the plugin manager to load all active plugins
    plugin_mgr = PluginManager(config)

    mapper = create_mapper(config, plugin_mgr.controller_scan)
    events.Environment.before_route_setup(mapper)
    add_routes(mapper)
    events.Environment.after_route_setup(mapper)
    config['routes.map'] = mapper
    config['pylons.app_globals'] = app_globals.Globals(config)
    config['pylons.app_globals'].plugin_mgr = plugin_mgr
    config['pylons.app_globals'].events = events
    config['pylons.h'] = mediadrop.lib.helpers

    # Setup cache object as early as possible
    pylons.cache._push_object(config['pylons.app_globals'].cache)

    config['locale_dirs'] = plugin_mgr.locale_dirs()
    config['locale_dirs'].update({
        'mediadrop': os.path.join(root, 'i18n'),
        'FormEncode': get_formencode_localedir(),
    })

    def enable_i18n_for_template(template):
        translations = Translator(translator)
        translations.setup(template)

    # Create the Genshi TemplateLoader
    config['pylons.app_globals'].genshi_loader = TemplateLoader(
        search_path=paths['templates'] + plugin_mgr.template_loaders(),
        auto_reload=True,
        max_cache_size=100,
        callback=enable_i18n_for_template,
    )

    # Setup the SQLAlchemy database engine
    engine = engine_from_config(config, 'sqlalchemy.')
    init_model(engine, config.get('db_table_prefix', None))
    events.Environment.init_model()

    # CONFIGURATION OPTIONS HERE (note: all config options will override
    #                                   any Pylons config options)

    # TODO: Move as many of these custom options into an .ini file, or at least
    #       to somewhere more friendly.

    # TODO: Rework templates not to rely on this line:
    #       See docstring in pylons.configuration.PylonsConfig for details.
    config['pylons.strict_tmpl_context'] = False

    config['thumb_sizes'] = { # the dimensions (in pixels) to scale thumbnails
        Media._thumb_dir: {
            's': (128,  72),
            'm': (160,  90),
            'l': (560, 315),
        },
        Podcast._thumb_dir: {
            's': (128, 128),
            'm': (160, 160),
            'l': (600, 600),
        },
    }

    # END CUSTOM CONFIGURATION OPTIONS

    events.Environment.loaded(config)

    return config
