#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This file is a part of MediaCore CE, Copyright 2009-2012 MediaCore Inc.
# The source code contained in this file is licensed under the GPL.
# See LICENSE.txt in the main project directory, for more information.
#
# Copyright (c) 2012 Felix Schwarz (www.schwarz.eu)


from mediacore.lib.test.db_testcase import DBTestCase
from mediacore.lib.test.pythonic_testcase import *
from mediacore.lib.test.request_mixin import RequestMixin


def suite():
    from mediacore.lib.auth.tests import (filtering_restricted_items_test, 
        group_based_permissions_policy_test, permission_system_test, 
        query_result_proxy_test, static_query_test)
    from mediacore.lib.tests import (css_delivery_test, js_delivery_test, 
        observable_test, request_mixin_test)
    from mediacore.lib.storage.tests import youtube_storage_test
    from mediacore.model.tests import (media_example_test, media_test, 
        user_example_test)
    from mediacore.plugin.tests import abstract_class_registration_test, events_test, observes_test
    
    from mediacore.validation.tests import limit_feed_items_validator_test
    
    # do not export 'unittest' via '*' import from this module
    import unittest
    suite = unittest.TestSuite()
    suite.addTest(abstract_class_registration_test.suite())
    suite.addTest(css_delivery_test.suite())
    suite.addTest(events_test.suite())
    suite.addTest(filtering_restricted_items_test.suite())
    suite.addTest(group_based_permissions_policy_test.suite())
    suite.addTest(limit_feed_items_validator_test.suite())
    suite.addTest(media_test.suite())
    suite.addTest(media_example_test.suite())
    suite.addTest(permission_system_test.suite())
    suite.addTest(observes_test.suite())
    suite.addTest(js_delivery_test.suite())
    suite.addTest(observable_test.suite())
    suite.addTest(query_result_proxy_test.suite())
    suite.addTest(request_mixin_test.suite())
    suite.addTest(static_query_test.suite())
    suite.addTest(user_example_test.suite())
    suite.addTest(youtube_storage_test.suite())
    return suite

if __name__ == '__main__':
    # do not export 'unittest' via '*' import from this module
    import unittest
    unittest.main(defaultTest='suite')
