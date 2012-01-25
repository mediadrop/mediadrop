# This file is a part of MediaCore CE, Copyright 2009-2012 MediaCore Inc.
# The source code contained in this file is licensed under the GPL.
# See LICENSE.txt in the main project directory, for more information.
import py.test

from mediacore import ipython
from mediacore.plugin.abc import AbstractClass, abstractmethod, abstractproperty, ImplementationError, _reset_registry

def pytest_funcarg__AbstractStuff(request):
    class AbstractStuff(AbstractClass):
        @abstractmethod
        def do_stuff(self):
            pass
    return AbstractStuff

def test_register(AbstractStuff):
    class StuffDoer(AbstractStuff):
        def do_stuff(self):
            return True
    AbstractStuff.register(StuffDoer)
    stuffs = list(AbstractStuff)
    assert len(stuffs) == 1
    assert stuffs[0] is StuffDoer
    _reset_registry()

def test_register_multiple_interfaces(AbstractStuff):
    class StuffDoer(AbstractStuff):
        def do_stuff(self):
            return True
    AbstractStuff.register(StuffDoer)

    class AbstractMoreStuff(AbstractStuff):
        @abstractmethod
        def do_more_stuff(self):
            pass
    class MoreStuffDoer(AbstractMoreStuff):
        def do_stuff(self):
            return True
        def do_more_stuff(self):
            return True
    AbstractMoreStuff.register(MoreStuffDoer)

    assert set(AbstractStuff) == set([StuffDoer, MoreStuffDoer])
    assert set(AbstractMoreStuff) == set([MoreStuffDoer])
    _reset_registry()

def test_implementation_checking(AbstractStuff):
    class StuffDoer(AbstractStuff):
        pass
    py.test.raises(ImplementationError, lambda: AbstractStuff.register(StuffDoer))
    _reset_registry()
