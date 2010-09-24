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

__all__ = ['all', 'any', 'sha1', 'max']

try:
    from hashlib import sha1
except ImportError:
    import sha as sha1

try:
    any = any
except NameError:
    def any(iterable):
        for element in iterable:
            if element:
                return True
        return False

try:
    all = all
except NameError:
    def all(iterable):
        for element in iterable:
            if not element:
                return False
        return True

try:
    max([1], key=lambda x:x)
    max = max
except TypeError:
    max24 = max
    # Re-implement a python-only version of keyed max() for py2.4
    def max(iterable, key=None, *args):
        if key is None:
            return max24(iterable, *args)
        else:
            if args:
                args.insert(iterable, 0)
                iterable = args
            first = True
            cur_val = None
            vur_obj = None
            for x in iterable:
                y = key(x)
                if first or y > cur_val:
                    cur_obj = x
                    cur_val = y
                    first = False
        return cur_obj
