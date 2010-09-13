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

from collections import defaultdict

class AbstractMetaClass(type):
    """
    Abstract Class Manager

    This combines concepts from the Trac ComponentMeta class and
    Python 2.6's abc module:

        * http://www.python.org/dev/peps/pep-3119/#specification
        * http://svn.python.org/view/python/trunk/Lib/abc.py?view=markup
        * http://trac.edgewall.org/browser/trunk/trac/core.py#L85

    """
    _registry = defaultdict(list)
    _abstracts = {}

    def __new__(mcls, name, bases, namespace):
        """Create a class object for an abstract class or its implementation.

        For abstract classes, we store the set of abstract attributes
        that have been defined. We use this data in :meth:`register`
        to validate all subclasses to ensure it has a complete
        implementation.

        """
        cls = type.__new__(mcls, name, bases, namespace)
        abstracts = set(key
                        for key, value in namespace.iteritems()
                        if getattr(value, '_isabstract', False))
        for base in bases:
            for name in AbstractMetaClass._abstracts.get(base, ()):
                cls_attr = getattr(cls, name, None)
                if getattr(cls_attr, '_isabstract', False):
                    abstracts.add(name)
        if abstracts:
            AbstractMetaClass._abstracts[cls] = abstracts
        return cls

    def register(cls, subclass):
        """Register an implementation of the abstract class.

        :param cls: The abstract class
        :param subclass: A complete implementation of the abstract class.
        :raises ImplementationError: If the subclass contains any
            unimplemented abstract methods or properties.

        """
        # Ensure all abstract methods have been implemented
        missing = []
        for name in AbstractMetaClass._abstracts.get(cls, ()):
            attr = getattr(subclass, name, None)
            if not attr or getattr(attr, '_isabstract', False):
                missing.append(name)
        if missing:
            raise ImplementationError(
                'Cannot register %r under %r because it contains abstract '
                'methods/properties: %s' % (subclass, cls, ', '.join(missing))
            )
        # Register the subclass for this abstract class and all its bases
        for base in cls.__mro__:
            if base.__class__ is AbstractMetaClass:
                AbstractMetaClass._registry[base].append(subclass)

    def __iter__(cls):
        """Iterate over all implementations of the given abstract class."""
        return iter(AbstractMetaClass._registry[cls])

    def __contains__(cls, subclass):
        """Return True if the first class is a parent of the second class."""
        return subclass in AbstractMetaClass._registry[cls]

class AbstractClass(object):
    """
    An optional base for abstract classes to subclass.
    """
    __metaclass__ = AbstractMetaClass

def abstractmethod(func):
    func._isabstract = True
    return func

class abstractproperty(property):
    _isabstract = True

class ImplementationError(Exception):
    """
    Error raised when a partial abstract class implementation is registered.
    """

def _reset_registry():
    AbstractMetaClass._registry.clear()
    AbstractMetaClass._abstracts.clear()
