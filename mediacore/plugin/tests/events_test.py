# This file is a part of MediaCore CE, Copyright 2009-2012 MediaCore Inc.
# The source code contained in this file is licensed under the GPL.
# See LICENSE.txt in the main project directory, for more information.
#
# Copyright (c) 2012 Felix Schwarz (www.schwarz.eu)

from mediacore.lib.test.pythonic_testcase import *

from mediacore.plugin.events import GeneratorEvent


class GeneratorEventTest(PythonicTestCase):
    def test_can_unroll_lists(self):
        event = GeneratorEvent([])
        event.observers.append(lambda: [1, 2, 3])
        event.observers.append(lambda: ('a', 'b'))
        
        assert_equals([1, 2, 3, 'a', 'b'], list(event()))
    
    def test_can_return_non_iterable_items(self):
        event = GeneratorEvent([])
        event.observers.append(lambda: [1, ])
        event.observers.append(lambda: None)
        event.observers.append(lambda: 5)
        event.observers.append(lambda: 'some value')
        
        assert_equals([1, None, 5, 'some value'], list(event()))



import unittest
def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(GeneratorEventTest))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='suite')
