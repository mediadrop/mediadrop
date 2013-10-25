# This file is a part of MediaDrop (http://www.mediadrop.net),
# Copyright 2009-2013 MediaDrop contributors
# For the exact contribution history, see the git revision log.
# The source code contained in this file is licensed under the GPLv3 or
# (at your option) any later version.
# See LICENSE.txt in the main project directory, for more information.

from mediacore.lib.test.pythonic_testcase import *

from mediacore.plugin.events import Event, observes
from mediacore.lib.decorators import observable


class ObservableDecoratorTest(PythonicTestCase):
    
    def probe(self, **result):
        result['probe'] = True
        return result
    
    def test_calls_observers_after_function_was_executed(self):
        event = Event([])
        observes(event)(self.probe)
        
        def function(*args, **kwargs):
            return {'args': list(args), 'kwargs': kwargs}
        decorated_function = observable(event)(function)
        
        result = decorated_function('foo', bar=True)
        assert_equals({'args': ['foo'], 'kwargs': {'bar': True}, 'probe': True},
                      result)
    
    def test_can_call_observers_before_executing_decorated_message(self):
        event = Event([])
        observes(event)(self.probe)
        def guard_probe(*args, **kwargs):
            assert_not_contains('probe', kwargs)
            kwargs['guard_probe'] = True
            return (args, kwargs)
        observes(event, run_before=True)(guard_probe)
        
        def function(*args, **kwargs):
            return {'args': list(args), 'kwargs': kwargs}
        decorated_function = observable(event)(function)
        
        expected = {
            'args': ['foo'], 
            'kwargs': {'bar': True, 'guard_probe': True}, 
            'probe': True
        }
        assert_equals(expected, decorated_function('foo', bar=True))


import unittest
def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ObservableDecoratorTest))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='suite')
