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
"""
Abstract events which plugins subscribe to and are called by the app.
"""
import logging
log = logging.getLogger(__name__)

class Event(object):
    """
    An arbitrary event that's triggered and observed by different parts of the app.

        >>> e = Event()
        >>> e.observers.append(lambda x: x)
        >>> e('x')

    """
    def __init__(self, args):
        self.args = args and frozenset(args) or None
        self.observers = []

    def __call__(self, *args, **kwargs):
        for observer in self.observers:
            observer(*args, **kwargs)

    def __iter__(self):
        return iter(self.observers)

class observes(object):
    """
    Register the decorated function as an observer of the given event.
    """
    def __init__(self, *events):
        self.events = events

    def __call__(self, func):
        for event in self.events:
            event.observers.append(func)
        return func

###############################################################################
# Application Setup

class Environment(object):
    routes = Event(['mapper'])
    loaded = Event(['config'])
