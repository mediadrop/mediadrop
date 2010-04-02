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

from tg.configuration import config
from routes import Mapper

def make_map():
    """Setup our custom named routes"""
    map = Mapper(directory=config['pylons.paths']['controllers'],
                 always_scan=config['debug'])

    #################
    # Public Routes #
    #################

    # Media list and non-specific actions
    # These are all mapped without any prefix to indicate the controller
    map.connect('/{action}',
        controller='media',
        action='index',
        requirements={'action': ('explore|upload|upload_submit|upload_success|'
                                 'upload_submit_async|upload_failure|index')})

    # Podcast list actions
    map.connect('/podcasts/feed/{slug}.xml',
        controller='podcasts',
        action='feed')
    map.connect('/podcasts/{slug}',
        controller='podcasts',
        action='view')

    # Category list actions
    map.connect('/tags/{slug}',
        controller='media',
        action='tags',
        slug=None)
    map.connect('/categories/{slug}',
        controller='categories',
        action='index',
        slug=None)

    # Individual media and actions their related actions
    map.connect('/view/{slug}/{action}',
        controller='media',
        action='view',
        requirements={'action': 'view|rate|comment'})
    map.connect('/files/{id}-{slug}.{type}',
        controller='media',
        action='serve',
        requirements={'id': r'\d+'})

    # Individual podcast media actions
    map.connect('/podcasts/{podcast_slug}/{slug}/{action}',
        controller='media',
        action='view',
        requirements={'action': 'view|rate|comment'})


    ################
    # Admin routes #
    ################

    admin_paths = "|".join([
        'admin/admin',
        'admin/categories',
        'admin/comments',
        'admin/display',
        'admin/media',
        'admin/notifications',
        'admin/podcasts',
        'admin/tags',
        'admin/users',
    ])

    map.connect('/admin', controller='admin/index', action='index')

    map.connect('/admin/media_table/{table}/{page}',
        controller='admin/admin',
        action='media_table')

    map.connect('{controller}',
        requirements = { 'controller': admin_paths }
    )

    map.connect('{controller}/{id}/{action}',
        requirements = {
            'controller': admin_paths,
            'id': r'\d+'
        },
        action='edit',
    )

    map.connect('{controller}/{action}',
        requirements = {'controller': admin_paths}
    )

    # TODO: Change how the save_status method works, so that it's two separate methods, and works with the above routes.
    map.connect('/admin/comments/{id}/{status}',
        controller='admin/comments',
        action='save_status',
        requirements={'status': 'approve|trash'})

    ##############
    # API routes #
    ##############

    map.connect('/api/media/{action}',
        controller='media_api',
        action='index')

    # Fallback Routes
    map.connect('/{controller}/{action}',
        action='index')

    # Set up object dispatch - this is required for TG's auth setup to work
    # FIXME: Look into this further...
    # Looks like routes.url_for doesn't work when using this route, so you
    # can't even switch back to routing. Argh.
    map.connect('*url',
        controller='root',
        action='routes_placeholder')

    return map
