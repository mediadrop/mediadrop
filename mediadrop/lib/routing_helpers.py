# -*- coding: utf-8 -*-
# This file is a part of MediaDrop (http://www.mediadrop.video),
# Copyright 2009-2015 MediaDrop contributors
# For the exact contribution history, see the git revision log.
# The source code in this file is dual licensed under the MIT license or
# the GPLv3 or (at your option) any later version.
# See LICENSE.txt in the main project directory, for more information.

from __future__ import absolute_import

import urlparse

from pylons.wsgiapp import PylonsApp

from .attribute_dict import AttrDict
from .helpers import url_for


__all__ = ['dispatch_info_for_url']

def dispatch_info_for_url(url, url_mapper):
    parsed_url = urlparse.urlparse(url)
    # "http://server.example" -> path: ''
    route_dict = url_mapper.match(url=parsed_url.path or '/')
    if not route_dict:
        return None
    controller_name = route_dict['controller']
    action_name = route_dict['action']
    controller = PylonsApp().find_controller(controller_name)
    if controller is None:
        return None
    action_method = getattr(controller, action_name, None)
    return AttrDict(
        controller=controller,
        action=action_method,
        controller_name=controller_name,
        action_name=action_name,
    )

def is_url_for_mediadrop_domain(url):
    """Return True if the host name part of the URL matches the host name of
    this MediaDrop instance. Disregards protocols (e.g. http/https), ports and
    paths."""
    root_url = url_for('/', qualified=True)
    instance_hostname = urlparse.urlparse(root_url).hostname
    url_hostname = urlparse.urlparse(url).hostname
    return (instance_hostname == url_hostname)
