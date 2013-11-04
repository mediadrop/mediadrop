# -*- coding: UTF-8 -*-

# License: Public Domain
# Authors: Felix Schwarz <felix.schwarz@oss.schwarz.eu>
# 
# Version 1.0

# 1.0 (06.02.2010)
#   - initial release

__all__ = ['AttrDict']


class AttrDict(dict):
    def __getattr__(self, name):
        if name not in self:
            raise AttributeError("'%s' object has no attribute '%s'" % (self.__class__.__name__, name))
        return self[name]


