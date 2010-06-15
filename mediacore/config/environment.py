# This file is a part of MediaCore, Copyright 2009 Simple Station Inc.
#
# MediaCore is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# MediaCore is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""Pylons environment configuration"""
import os
import re

from genshi.filters.i18n import Translator
from genshi.template import TemplateLoader
from pylons.configuration import PylonsConfig
from pylons.i18n.translation import ugettext
from sqlalchemy import engine_from_config

import mediacore.lib.app_globals as app_globals
import mediacore.lib.helpers

from mediacore.config.routing import make_map
from mediacore.lib.auth import classifier_for_flash_uploads
from mediacore.model import User, Group, Permission, init_model
from mediacore.model.meta import DBSession

def load_environment(global_conf, app_conf):
    """Configure the Pylons environment via the ``pylons.config``
    object
    """
    config = PylonsConfig()

    # Pylons paths
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    paths = dict(root=root,
                 controllers=os.path.join(root, 'controllers'),
                 static_files=os.path.join(root, 'public'),
                 templates=[os.path.join(root, 'templates')])

    # Initialize config with the basic options
    config.init_app(global_conf, app_conf, package='mediacore', paths=paths)

    config['routes.map'] = make_map(config)
    config['pylons.app_globals'] = app_globals.Globals(config)
    config['pylons.h'] = mediacore.lib.helpers

    # Setup cache object as early as possible
    import pylons
    pylons.cache._push_object(config['pylons.app_globals'].cache)


    translator = Translator(ugettext)
    def enable_i18n_for_template(template):
        template.filters.insert(0, translator)

    # Create the Genshi TemplateLoader
    config['pylons.app_globals'].genshi_loader = TemplateLoader(
        search_path=paths['templates'],
        auto_reload=True,
        callback=enable_i18n_for_template
    )

    # Setup the SQLAlchemy database engine
    engine = engine_from_config(config, 'sqlalchemy.')
    init_model(engine)

    # CONFIGURATION OPTIONS HERE (note: all config options will override
    # any Pylons config options)
    # TODO: Move as many of these custom options into an .ini file, or at least
    # to somewhere more friendly.

    # TODO: rework templates not to rely on this line:
    # See docstring in pylons.configuration.PylonsConfig for details.
    config['pylons.strict_tmpl_context'] = False

    # Genshi Default Search Path
    config['genshi_search_path'] = paths['templates'][0]

    config['thumb_sizes'] = { # the dimensions (in pixels) to scale thumbnails
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

    # The max number of results to return for any api listing
    config['api_media_max_results'] = 50

    # END CUSTOM CONFIGURATION OPTIONS

    return config

def load_batch_environment(config_dir, config_file):
    """Set up a simple environment for executing batch scripts.

    This will provide access to the SQLAlchemy models, and to
    pylons.config.
    """

    # Load the application config
    from paste.deploy import appconfig
    conf = appconfig('config:'+config_file, relative_to=config_dir)

    # Load the logging options
    # (must be done before environment is loaded or sqlalchemy won't log)
    from paste.script.util.logging_config import fileConfig
    fileConfig(config_dir+os.sep+config_file)

    # Load the environment
    config = load_environment(conf.global_conf, conf.local_conf)

    # Set up globals for helper libs to use (like pylons.config)
    from paste.registry import Registry
    import pylons
    reg = Registry()
    reg.prepare()
    reg.register(pylons.config, config)
