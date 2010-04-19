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
"""Routes configuration

The more specific and detailed routes should be defined first so they
may take precedent over the more generic routes. For more information
refer to the routes manual at http://routes.groovie.org/docs/
"""
from routes import Mapper

def make_map(config):
    """Create, configure and return the routes Mapper"""
    map = Mapper(directory=config['pylons.paths']['controllers'],
                 always_scan=config['debug'])
    map.minimization = True # TODO: Rework routes so we can set this to False

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


    ###############
    # Auth Routes #
    ###############

    # XXX: These URLs are hardcoded into mediacore.lib.auth and
    # mediacore.templates.login.html. These files are initialized before
    # routing helper methods (ie pylons.url) are available.
    map.connect('/login', controller='login', action='login')
    map.connect('/login/submit', controller='login', action='login_handler')
    map.connect('/login/continue', controller='login', action='post_login')
    map.connect('/logout/continue', controller='login', action='post_logout')
    map.connect('/logout', controller='login', action='logout_handler')


    ################
    # Admin routes #
    ################

    map.connect('/admin',
        controller='admin/index',
        action='index')

    map.connect('/admin/index',
        controller='admin/index',
        action='index')

    map.redirect('/admin/settings', '/admin/settings/categories',
        _redirect_code='301 Moved Permanently')

    map.connect('/admin/settings/categories',
        controller='admin/categories',
        action='index')
    map.connect('/admin/settings/categories/{id}/{action}',
        controller='admin/categories',
        action='edit',
        requirements={'id': r'(\d+|new)'})

    map.connect('/admin/settings/tags',
        controller='admin/tags',
        action='index')
    map.connect('/admin/settings/tags/{id}/{action}',
        controller='admin/tags',
        action='edit',
        requirements={'id': r'(\d+|new)'})

    map.connect('/admin/settings/users',
        controller='admin/users',
        action='index')
    map.connect('/admin/settings/users/{id}/{action}',
        controller='admin/users',
        action='edit',
        requirements={'id': r'(\d+|new)'})

    map.connect('/admin/comments/{id}/{status}',
        controller='admin/comments',
        action='save_status',
        requirements={'status': 'approve|trash'})


    simple_admin_paths = '|'.join([
        'admin/index',
        'admin/comments',
        'admin/media',
        'admin/podcasts',
    ])

    map.connect('/{controller}',
        action='index',
        requirements={'controller': simple_admin_paths})

    map.connect('/{controller}/{id}/{action}',
        action='edit',
        requirements={'controller': simple_admin_paths, 'id': r'(\d+|new)'})

    map.connect('/{controller}/{action}',
        requirements={'controller': simple_admin_paths})

    ##############
    # API routes #
    ##############

    map.connect('/api/media/{action}',
        controller='media_api',
        action='index')

    ##################
    # Fallback Route #
    ##################
    map.connect('/{controller}/{action}', action='index')

    return map
