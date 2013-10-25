# This file is a part of MediaDrop (http://www.mediadrop.net),
# Copyright 2009-2013 MediaDrop contributors
# For the exact contribution history, see the git revision log.
# The source code contained in this file is licensed under the GPLv3 or
# (at your option) any later version.
# See LICENSE.txt in the main project directory, for more information.

"""Routes configuration

The more specific and detailed routes should be defined first so they
may take precedent over the more generic routes. For more information
refer to the routes manual at http://routes.groovie.org/docs/
"""
from routes import Mapper
from routes.util import controller_scan

login_form_url = '/login'
login_handler_url = '/login/submit'
logout_handler_url = '/logout'
post_login_url = '/login/continue'
post_logout_url = '/logout/continue'

def create_mapper(config, controller_scan=controller_scan):
    """Create, configure and return the routes Mapper"""
    map = Mapper(controller_scan=controller_scan,
                 directory=config['pylons.paths']['controllers'],
                 always_scan=config['debug'])
    map.explicit = False
    map.minimization = True # TODO: Rework routes so we can set this to False
    return map

def add_routes(map):
    #################
    # Public Routes #
    #################

    # Media list and non-specific actions
    # These are all mapped without any prefix to indicate the controller
    map.connect('/', controller='media', action='explore')
    map.connect('/media', controller='media', action='index')
    map.connect('/random', controller='media', action='random')

    # Podcasts
    map.connect('/podcasts/feed/{slug}.xml',
        controller='podcasts',
        action='feed')
    map.connect('/podcasts/{slug}',
        controller='podcasts',
        action='view')

    # Sitemaps
    map.connect('/sitemap.xml',
        controller='sitemaps',
        action='google')
    map.connect('/latest.xml',
        controller='sitemaps',
        action='latest')
    map.connect('/featured.xml',
        controller='sitemaps',
        action='featured')
    map.connect('/sitemap{page}.xml',
        controller='sitemaps',
        action='google',
        requirements={'page': r'\d+'})
    map.connect('/mrss.xml',
        controller='sitemaps',
        action='mrss')
    map.connect('/crossdomain.xml',
        controller='sitemaps',
        action='crossdomain_xml')

    # Categories
    map.connect('/categories/feed/{slug}.xml',
        controller='categories',
        action='feed')
    map.connect('/categories/{slug}',
        controller='categories',
        action='index',
        slug=None)
    map.connect('/categories/{slug}/{order}',
        controller='categories',
        action='more',
        requirements={'order': 'latest|popular'})

    # Tags
    map.connect('/tags',
        controller='media',
        action='tags')
    map.connect('/tags/{tag}',
        controller='media',
        action='index')

    # Media
    map.connect('/media/{slug}/{action}',
        controller='media',
        action='view')
    map.connect('/files/{id}-{slug}.{container}',
        controller='media',
        action='serve',
        requirements={'id': r'\d+'})
    map.connect('static_file_url', '/files/{id}.{container}',
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

    # XXX: These URLs are also hardcoded at the top of this file
    # This file is initialized by the auth middleware before routing helper
    # methods (ie pylons.url) are available.
    map.connect(login_form_url, controller='login', action='login')
    map.connect(login_handler_url, controller='login', action='login_handler')
    map.connect(logout_handler_url, controller='login', action='logout_handler')
    map.connect(post_login_url, controller='login', action='post_login')
    map.connect(post_logout_url, controller='login', action='post_logout')


    ################
    # Admin routes #
    ################

    map.connect('/admin',
        controller='admin/index',
        action='index')

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

    map.connect('/admin/users',
        controller='admin/users',
        action='index')
    map.connect('/admin/users/{id}/{action}',
        controller='admin/users',
        action='edit',
        requirements={'id': r'(\d+|new)'})
    
    map.connect('/admin/groups',
        controller='admin/groups',
        action='index')
    map.connect('/admin/groups/{id}/{action}',
        controller='admin/groups',
        action='edit',
        requirements={'id': r'(\d+|new)'})

    map.connect('/admin/settings/players',
        controller='admin/players',
        action='index')
    map.connect('/admin/settings/players/{id}/{action}',
        controller='admin/players',
        action='edit',
        requirements={'id': r'(\d+|new)'})

    map.connect('/admin/settings/storage',
        controller='admin/storage',
        action='index')
    map.connect('/admin/settings/storage/{id}/{action}',
        controller='admin/storage',
        action='edit',
        requirements={'id': r'(\d+|new)'})

    map.connect('/admin/media/bulk/{type}',
        controller='admin/media',
        action='bulk')

    map.connect('/admin/media/merge_stubs',
        controller='admin/media',
        action='merge_stubs')


    simple_admin_paths = '|'.join([
        'admin/index',
        'admin/comments',
        'admin/media',
        'admin/podcasts',
        'admin/settings',
    ])

    map.connect('/{controller}',
        action='index',
        requirements={'controller': simple_admin_paths})

    map.connect('/{controller}/{id}/{action}',
        action='edit',
        requirements={'controller': simple_admin_paths, 'id': r'(\d+|new|bulk)'})

    map.connect('/{controller}/{action}',
        requirements={'controller': simple_admin_paths})

    ##############
    # API routes #
    ##############

    map.connect('/api/media/{action}',
        controller='api/media',
        action='index')

    map.connect('/api/categories/{action}',
        controller='api/categories',
        action='index')

    ##################
    # Fallback Route #
    ##################
    map.connect('/{controller}/{action}', action='index')

    return map
