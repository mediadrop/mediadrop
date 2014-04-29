# This file is a part of MediaDrop (http://www.mediadrop.net),
# Copyright 2009-2014 MediaDrop contributors
# For the exact contribution history, see the git revision log.
# The source code contained in this file is licensed under the GPLv3 or
# (at your option) any later version.
# See LICENSE.txt in the main project directory, for more information.

from mediadrop.lib.test.pythonic_testcase import *

from mediadrop.plugin.events import Event, FetchFirstResultEvent, GeneratorEvent


class EventTest(PythonicTestCase):
    def setUp(self):
        self.observers_called = 0
        self.event = Event()
    
    def probe(self):
        self.observers_called += 1
    
    def test_can_notify_all_observers(self):
        self.event.post_observers.append(self.probe)
        self.event.pre_observers.append(self.probe)
        
        assert_equals(0, self.observers_called)
        self.event()
        assert_equals(2, self.observers_called)


class FetchFirstResultEventTest(PythonicTestCase):
    def test_returns_first_non_null_result(self):
        event = FetchFirstResultEvent([])
        event.post_observers.append(lambda: None)
        event.post_observers.append(lambda: 1)
        event.post_observers.append(lambda: 2)
        
        assert_equals(1, event())
    
    def test_passes_all_event_parameters_to_observers(self):
        event = FetchFirstResultEvent([])
        event.post_observers.append(lambda foo, bar=None: foo)
        event.post_observers.append(lambda foo, bar=None: bar or foo)
        
        assert_equals(4, event(4))
        assert_equals(6, event(None, bar=6))


class GeneratorEventTest(PythonicTestCase):
    def test_can_unroll_lists(self):
        event = GeneratorEvent([])
        event.post_observers.append(lambda: [1, 2, 3])
        event.post_observers.append(lambda: ('a', 'b'))
        
        assert_equals([1, 2, 3, 'a', 'b'], list(event()))
    
    def test_can_return_non_iterable_items(self):
        event = GeneratorEvent([])
        event.post_observers.append(lambda: [1, ])
        event.post_observers.append(lambda: None)
        event.post_observers.append(lambda: 5)
        event.post_observers.append(lambda: 'some value')
        
        assert_equals([1, None, 5, 'some value'], list(event()))



import unittest
def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(EventTest))
    suite.addTest(unittest.makeSuite(FetchFirstResultEventTest))
    suite.addTest(unittest.makeSuite(GeneratorEventTest))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='suite')
