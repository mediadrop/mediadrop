import socket
import struct


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
        return other.name == self.name and other.email == self.name

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        return '<Author: "%s">' % self.name


class AuthorWithIP(Author):
    """Author Info Wrapper with an extra column for an IP"""
    def __init__(self, name=None, email=None, ip=None):
        super(AuthorWithIP, self).__init__(name, email)
        self.ip = ip

    def __composite_values__(self):
        values = super(AuthorWithIP, self).__composite_values__()
        values.append(self._ip)
        return values

    def __eq__(self, other):
        return super(AuthorWithIP, self).__eq__(other) and self._ip == other._ip

    def _set_ip(self, ip):
        if ip is None or isinstance(ip, (int, long)):
            self._ip = None
        else:
            self._ip = struct.unpack('!L', socket.inet_aton(ip))[0]

    def _get_ip(self):
        if self._ip is None:
            return None
        return socket.inet_ntoa(struct.pack('!L', self._ip))

    ip = property(_get_ip, _set_ip)


if __name__ == '__main__':
    inip = '255.255.255.255'
    a = AuthorWithIP('Name', 'Email', inip)
    print 'In ', inip
    a.ip = inip
    print a.ip
    print a._ip
