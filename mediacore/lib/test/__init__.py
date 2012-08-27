#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This file is a part of MediaCore CE, Copyright 2009-2012 MediaCore Inc.
# The source code contained in this file is licensed under the GPL.
# See LICENSE.txt in the main project directory, for more information.
#
# Copyright (c) 2012 Felix Schwarz (www.schwarz.eu)


import unittest

def suite():
    from mediacore.plugin.tests import events_test, observes_test
    from mediacore.lib.tests import js_delivery_test, observable_test
    
    suite = unittest.TestSuite()
    suite.addTest(events_test.suite())
    suite.addTest(observes_test.suite())
    suite.addTest(js_delivery_test.suite())
    suite.addTest(observable_test.suite())
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='suite')
