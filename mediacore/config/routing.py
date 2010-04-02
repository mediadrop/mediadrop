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
    map.connect('/', controller='media', action='explore')
    map.connect('/media', controller='media', action='index')

    # TODO: Refactor into media/index
    map.connect('/search', controller='media', action='search')

    # Podcasts
    map.connect('/podcasts/feed/{slug}.xml',
        controller='podcasts',
        action='feed')
    map.connect('/podcasts/{slug}',
        controller='podcasts',
        action='view')

    # Categories
    map.connect('/categories/{slug}',
        controller='categories',
        action='index',
        slug=None)
    map.connect('/categories/{slug}/{order}',
        controller='categories',
        action='more',
        requirements={'order': 'latest|popular'})

    # Media
    map.connect('/media/{slug}/{action}',
        controller='media',
        action='view')
    map.connect('/files/{id}-{slug}.{type}',
        controller='media',
        action='serve',
        requirements={'id': r'\d+'})
    map.connect('/upload/{action}',
        controller='upload',
        action='index')

    # Podcast Episodes
    map.connect('/podcasts/{podcast_slug}/{slug}/{action}',
        controller='media',
        action='view',
        requirements={'action': 'view|rate|comment'})


    ################
    # Admin routes #
    ################

    map.connect('/admin/media_table/{table}/{page}',
        controller='admin',
        action='media_table')

    map.connect('/admin/media',
        controller='mediaadmin',
        action='index')
    map.connect('/admin/media/{id}/{action}',
        controller='mediaadmin',
        action='edit')

    map.connect('/admin/podcasts',
        controller='podcastadmin',
        action='index')
    map.connect('/admin/podcasts/{id}/{action}',
        controller='podcastadmin',
        action='edit')

    map.connect('/admin/comments',
        controller='commentadmin',
        action='index')
    map.connect('/admin/comments/{id}/{status}',
        controller='commentadmin',
        action='save_status',
        requirements={'status': 'approve|trash'})

    map.connect('/admin/settings',
        controller='settingadmin',
        action='index')

    map.connect('/admin/settings/config/{action}',
        controller='settingadmin',
        action='edit')

    map.connect('/admin/settings/users',
        controller='useradmin',
        action='index')
    map.connect('/admin/settings/users/{id}/{action}',
        controller='useradmin',
        action='edit')

    map.connect('/admin/settings/tags',
        controller='tagadmin',
        action='index')
    map.connect('/admin/settings/tags/{id}/{action}',
        controller='tagadmin',
        action='edit')
    map.connect('/admin/settings/categories',
        controller='categoryadmin',
        action='index')
    map.connect('/admin/settings/categories/{id}/{action}',
        controller='categoryadmin',
        action='edit')

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
