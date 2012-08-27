# This file is a part of MediaCore CE, Copyright 2009-2012 MediaCore Inc.
# The source code contained in this file is licensed under the GPL.
# See LICENSE.txt in the main project directory, for more information.
#
# Copyright (c) 2012 Felix Schwarz (www.schwarz.eu)

from mediacore.lib.test.pythonic_testcase import *

from mediacore.plugin.events import Event, observes


class ObserveDecoratorTest(PythonicTestCase):
    
    def probe(self, result):
        pass
    
    def test_can_observe_event(self):
        event = Event([])
        observes(event)(self.probe)
        
        assert_length(1, event.observers)
        assert_equals(self.probe, event.observers[0])
    
    def test_observers_can_request_priority(self):
        def second_probe(result):
            pass
        event = Event([])
        observes(event)(self.probe)
        observes(event, appendleft=True)(second_probe)
        
        assert_length(2, event.observers)
        assert_equals([second_probe, self.probe], list(event.observers))


import unittest
def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ObserveDecoratorTest))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='suite')
