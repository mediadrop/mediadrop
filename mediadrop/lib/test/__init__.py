#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This file is a part of MediaDrop (http://www.mediadrop.net),
# Copyright 2009-2013 MediaDrop contributors
# For the exact contribution history, see the git revision log.
# The source code contained in this file is licensed under the GPLv3 or
# (at your option) any later version.
# See LICENSE.txt in the main project directory, for more information.


from mediadrop.lib.test.controller_testcase import *
from mediadrop.lib.test.db_testcase import DBTestCase
from mediadrop.lib.test.pythonic_testcase import *
from mediadrop.lib.test.request_mixin import *
from mediadrop.lib.test.support import *


def suite():
    from mediadrop.controllers.tests import login_test, upload_test
    from mediadrop.lib.auth.tests import (filtering_restricted_items_test, 
        group_based_permissions_policy_test, mediadrop_permission_system_test,
        permission_system_test, query_result_proxy_test, static_query_test)
    from mediadrop.lib.tests import (css_delivery_test, current_url_test,
        helpers_test, js_delivery_test, observable_test, request_mixin_test,
        url_for_test, xhtml_normalization_test)
    from mediadrop.lib.storage.tests import youtube_storage_test
    from mediadrop.model.tests import (category_example_test, group_example_test, 
        media_example_test, media_status_test, media_test, user_example_test)
    from mediadrop.plugin.tests import abstract_class_registration_test, events_test, observes_test
    
    from mediadrop.validation.tests import (limit_feed_items_validator_test, 
        uri_validator_test)
    
    # do not export 'unittest' via '*' import from this module
    import unittest
    suite = unittest.TestSuite()
    suite.addTest(abstract_class_registration_test.suite())
    suite.addTest(category_example_test.suite())
    suite.addTest(css_delivery_test.suite())
    suite.addTest(current_url_test.suite())
    suite.addTest(events_test.suite())
    suite.addTest(filtering_restricted_items_test.suite())
    suite.addTest(group_based_permissions_policy_test.suite())
    suite.addTest(group_example_test.suite())
    suite.addTest(helpers_test.suite())
    suite.addTest(limit_feed_items_validator_test.suite())
    suite.addTest(login_test.suite())
    suite.addTest(media_example_test.suite())
    suite.addTest(media_status_test.suite())
    suite.addTest(media_test.suite())
    suite.addTest(mediadrop_permission_system_test.suite())
    suite.addTest(permission_system_test.suite())
    suite.addTest(observes_test.suite())
    suite.addTest(js_delivery_test.suite())
    suite.addTest(observable_test.suite())
    suite.addTest(query_result_proxy_test.suite())
    suite.addTest(request_mixin_test.suite())
    suite.addTest(static_query_test.suite())
    suite.addTest(upload_test.suite())
    suite.addTest(uri_validator_test.suite())
    suite.addTest(url_for_test.suite())
    suite.addTest(user_example_test.suite())
    suite.addTest(youtube_storage_test.suite())
    suite.addTest(xhtml_normalization_test.suite())
    return suite

if __name__ == '__main__':
    # do not export 'unittest' via '*' import from this module
    import unittest
    unittest.main(defaultTest='suite')
