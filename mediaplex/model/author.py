class Author(object):
    def __init__(self, name=None, email=None, ip=None):
        self.name = name
        self.email = email
        self.ip = ip

    def __composite_values__(self):
        return [self.name, self.email, self.ip]

    def __eq__(self, other):
        return other.name == self.name and other.email == self.name

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        return '<Author: "%s">' % self.name

    def _set_ip(self, ip):
        self._ip = ip
    def _get_ip(self):
        return self._ip
    ip = property(_get_ip, _set_ip)

#>>> # change each decimal portion of IP address to hex pair
#>>> hexn = ''.join(["%02X" % long(i) for i in ip.split('.')])
#>>> long(hexn, 16)
#3232236033L

