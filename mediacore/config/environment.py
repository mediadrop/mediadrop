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
from mediacore.model import Media, Podcast, init_model
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
    init_model(engine, config.get('db_table_prefix', None))

    # CONFIGURATION OPTIONS HERE (note: all config options will override
    # any Pylons config options)
    # TODO: Move as many of these custom options into an .ini file, or at least
    # to somewhere more friendly.

    # TODO: rework templates not to rely on this line:
    # See docstring in pylons.configuration.PylonsConfig for details.
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

    # The max number of results to return for any api listing
    config['api_media_max_results'] = 50

    # END CUSTOM CONFIGURATION OPTIONS

    return config
