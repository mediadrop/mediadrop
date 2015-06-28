# -*- coding: UTF-8 -*-
# Copyright 2013 Felix Friedrich, Felix Schwarz
# Copyright 2015 Felix Schwarz
# The source code in this file is licensed under the MIT license.


__all__ = ['Result']

class Result(object):
    def __init__(self, value, **data):
        self.value = value
        self.data = data

    def __repr__(self):
        klassname = self.__class__.__name__
        extra_data = [repr(self.value)]
        for key, value in sorted(self.data.items()):
            extra_data.append('%s=%r' % (key, value))
        return '%s(%s)' % (klassname, ', '.join(extra_data))

    def __eq__(self, other):
        if isinstance(other, self.value.__class__):
            return self.value == other
        elif hasattr(other, 'value'):
            return self.value == other.value
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __bool__(self):
        return self.value
    # Python 2 compatibility
    __nonzero__ = __bool__

    def __getattr__(self, key):
        if key in self.data:
            return self.data[key]
        elif key.startswith('set_'):
            attr_name = key[4:]
            if attr_name in self.data:
                return self.__build_setter(attr_name)
        klassname = self.__class__.__name__
        msg = '%r object has no attribute %r' % (klassname, key)
        raise AttributeError(msg)

    def __build_setter(self, attr_name):
        def setter(value):
            self.data[attr_name] = value
        setter.__name__ = 'set_'+attr_name
        return setter

