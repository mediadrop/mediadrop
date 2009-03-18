class Author(object):
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
