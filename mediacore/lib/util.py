# This file is a part of MediaDrop (http://www.mediadrop.net),
# Copyright 2009-2013 MediaDrop contributors
# For the exact contribution history, see the git revision log.
# The source code contained in this file is licensed under the GPLv3 or
# (at your option) any later version.
# See LICENSE.txt in the main project directory, for more information.
"""
Library Utilities

"""
import math
import os
import shutil
from datetime import datetime
from urlparse import urlparse

from pylons import app_globals, config, request, url as pylons_url
from webob.exc import HTTPFound

__all__ = [
    'calculate_popularity',
    'current_url',
    'delete_files',
    'merge_dicts',
    'redirect',
    'url',
    'url_for',
    'url_for_media',
]

def current_url(with_qs=True, qualified=True):
    """This method returns the "current" (as in "url as request by the user")
    url.
    
    The default "url_for()" returns the current URL in most cases however when
    the error controller is triggered "url_for()" will return the url of the
    error document ('<host>/error/document') instead of the url requested by the
    user."""
    original_request = request.environ.get('pylons.original_request')
    if original_request:
        request_ = original_request
        url_generator = original_request.environ.get('routes.url')
        url = url_generator.current(qualified=qualified)
    else:
        request_ = request
        url = url_for(qualified=qualified)
    query_string = request_.environ.get('QUERY_STRING')
    if with_qs and query_string:
        return url + '?' + query_string
    return url

def url(*args, **kwargs):
    """Compose a URL with :func:`pylons.url`, all arguments are passed."""
    return _generate_url(pylons_url, *args, **kwargs)

def url_for(*args, **kwargs):
    """Compose a URL :func:`pylons.url.current`, all arguments are passed."""
    return _generate_url(pylons_url.current, *args, **kwargs)

# Mirror the behaviour you'd expect from pylons.url
url.current = url_for

def url_for_media(media, qualified=False):
    """Return the canonical URL for that media ('/media/view')."""
    return url_for(controller='/media', action='view', slug=media.slug, qualified=qualified)

def _generate_url(url_func, *args, **kwargs):
    """Generate a URL using the given callable."""
    # Convert unicode to str utf-8 for routes
    def to_utf8(value):
        if isinstance(value, unicode):
            return value.encode('utf-8')
        return value

    if args:
        args = [to_utf8(val) for val in args]
    if kwargs:
        kwargs = dict((key, to_utf8(val)) for key, val in kwargs.iteritems())

    # TODO: Rework templates so that we can avoid using .current, and use named
    # routes, as described at http://routes.readthedocs.org/en/latest/generating.html#generating-routes-based-on-the-current-url
    # NOTE: pylons.url is a StackedObjectProxy wrapping the routes.url method.
    url = url_func(*args, **kwargs)

    # If the proxy_prefix config directive is set up, then we need to make sure
    # that the SCRIPT_NAME is prepended to the URL. This SCRIPT_NAME prepending
    # is necessary for mod_proxy'd deployments, and for FastCGI deployments.
    # XXX: Leaking abstraction below. This code is tied closely to Routes 1.12
    #      implementation of routes.util.URLGenerator.__call__()
    # If the arguments given didn't describe a raw URL, then Routes 1.12 didn't
    # prepend the SCRIPT_NAME automatically--we'll need to feed the new URL
    # back to the routing method to prepend the SCRIPT_NAME.
    prefix = config.get('proxy_prefix', None)
    script_name = request.environ.get('SCRIPT_NAME', None)
    if prefix and (prefix != script_name):
        if args:
            named_route = config['routes.map']._routenames.get(args[0])
            protocol = urlparse(args[0]).scheme
            static = not named_route and (args[0][0]=='/' or protocol)
        else:
            static = False
            protocol = ''

        if not static:
            if kwargs.get('qualified', False):
                offset = len(urlparse(url).scheme+"://")
            else:
                offset = 0
            path_index = url.index('/', offset)
            url = url[:path_index] + prefix + url[path_index:]

    return url

def redirect(*args, **kwargs):
    """Compose a URL using :func:`url_for` and raise a redirect.

    :raises: :class:`webob.exc.HTTPFound`
    """
    url = url_for(*args, **kwargs)
    raise HTTPFound(location=url)

def delete_files(paths, subdir=None):
    """Move the given files to the 'deleted' folder, or just delete them.

    If the config contains a deleted_files_dir setting, then files are
    moved there. If that setting does not exist, or is empty, then the
    files will be deleted permanently instead.

    :param paths: File paths to delete. These files do not necessarily
        have to exist.
    :type paths: iterable
    :param subdir: A subdir within the configured deleted_files_dir to
        move the given files to. If this folder does not yet exist, it
        will be created.
    :type subdir: str or ``None``

    """
    deleted_dir = config.get('deleted_files_dir', None)
    if deleted_dir and subdir:
        deleted_dir = os.path.join(deleted_dir, subdir)
    if deleted_dir and not os.path.exists(deleted_dir):
        os.mkdir(deleted_dir)
    for path in paths:
        if path and os.path.exists(path):
            if deleted_dir:
                shutil.move(path, deleted_dir)
            else:
                os.remove(path)

def merge_dicts(dst, *srcs):
    """Recursively merge two or more dictionaries.

    Code adapted from Manuel Muradas' example at
    http://code.activestate.com/recipes/499335-recursively-update-a-dictionary-without-hitting-py/
    """
    for src in srcs:
        stack = [(dst, src)]
        while stack:
            current_dst, current_src = stack.pop()
            for key in current_src:
                if key in current_dst \
                and isinstance(current_src[key], dict) \
                and isinstance(current_dst[key], dict):
                    stack.append((current_dst[key], current_src[key]))
                else:
                    current_dst[key] = current_src[key]
    return dst

def calculate_popularity(publish_date, score):
    """Calculate how 'hot' an item is given its response since publication.

    In our ranking algorithm, being base_life_hours newer is equivalent
    to having log_base times more votes.

    :type publish_date: datetime.datetime
    :param publish_date: The date of publication. An older date reduces
        the popularity score.
    :param int score: The number of likes, dislikes or likes - dislikes.
    :rtype: int
    :returns: Popularity points.

    """
    settings = request.settings
    log_base = int(settings['popularity_decay_exponent'])
    base_life = int(settings['popularity_decay_lifetime']) * 3600
    # FIXME: The current algorithm assumes that the earliest publication
    #        date is January 1, 2000.
    if score > 0:
        sign = 1
    elif score < 0:
        sign = -1
    else:
        sign = 0
    delta = publish_date - datetime(2000, 1, 1) # since January 1, 2000
    t = delta.days * 86400 + delta.seconds
    popularity = math.log(max(abs(score), 1), log_base) + sign * t / base_life
    return max(int(popularity), 0)
