# This file is a part of MediaCore CE, Copyright 2009-2012 MediaCore Inc.
# The source code contained in this file is licensed under the GPL.
# See LICENSE.txt in the main project directory, for more information.
#
# Copyright (c) 2012 Felix Schwarz (www.schwarz.eu)

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


import unittest
def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ObservableDecoratorTest))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='suite')
