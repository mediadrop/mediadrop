# This file is a part of MediaDrop (http://www.mediadrop.net),
# Copyright 2009-2013 MediaDrop contributors
# For the exact contribution history, see the git revision log.
# The source code contained in this file is licensed under the GPLv3 or
# (at your option) any later version.
# See LICENSE.txt in the main project directory, for more information.

import socket
import struct
from mediadrop.lib.compat import inet_aton


class Author(object):
    """Basic Author Info Wrapper

    Intended to standardize access to author data across various models
    as if we were using a separate 'authors' table. Someday we will need
    to do that, so we might as well write all our controller/view code to
    handle that from the get go.

    """
    def __init__(self, name=None, email=None):
        self.name = name
        self.email = email

    def __composite_values__(self):
        return [self.name, self.email]

    def __eq__(self, other):
        if isinstance(other, Author):
            return self.name == other.name and self.email == other.email
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        return '<Author: %r>' % self.name


def _pack_ip(ip_dot_str):
    """Convert an IP address string in dot notation to an 32-bit integer"""
    if not ip_dot_str:
        return None
    return struct.unpack('!L', inet_aton(str(ip_dot_str)))[0]

def _unpack_ip(ip_int):
    """Convert an 32-bit integer IP to a dot-notated string"""
    if not ip_int:
        return None
    return socket.inet_ntoa(struct.pack('!L', long(ip_int)))


class AuthorWithIP(Author):
    """Author Info Wrapper with an extra column for an IP"""
    def __init__(self, name=None, email=None, ip=None):
        super(AuthorWithIP, self).__init__(name, email)
        self.ip = ip

    def __composite_values__(self):
        values = super(AuthorWithIP, self).__composite_values__()
        values.append(_pack_ip(self.ip))
        return values

    def __eq__(self, other):
        if isinstance(other, AuthorWithIP):
            return super(AuthorWithIP, self).__eq__(other) and self.ip == other.ip
        return False

    def __repr__(self):
        return '<Author: %r %s>' % (self.name, self.ip)

    def _get_ip(self):
        return getattr(self, '_ip', None)

    def _set_ip(self, value):
        try:
            self._ip = _unpack_ip(value)
        except:
            self._ip = value

    ip = property(_get_ip, _set_ip)
