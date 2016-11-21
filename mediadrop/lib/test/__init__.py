#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This file is a part of MediaDrop (http://www.mediadrop.video),
# Copyright 2009-2015 MediaDrop contributors
# For the exact contribution history, see the git revision log.
# The source code contained in this file is licensed under the GPLv3 or
# (at your option) any later version.
# See LICENSE.txt in the main project directory, for more information.

import sys

from mediadrop.lib.test.controller_testcase import *
from mediadrop.lib.test.db_testcase import DBTestCase
from mediadrop.lib.test.pythonic_testcase import *
from mediadrop.lib.test.request_mixin import *
from mediadrop.lib.test.support import *


def suite():
    from mediadrop.controllers.tests import login_test, upload_test
    from mediadrop.lib.auth.tests import (
        cookieplugin_test,
        filtering_restricted_items_test,
        group_based_permissions_policy_test,
        is_logged_in_decorator_test,
        loginform_test,
        mediadrop_permission_system_test,
        permission_system_test, query_result_proxy_test, static_query_test)
    from mediadrop.lib.tests import (css_delivery_test, current_url_test,
        helpers_test, human_readable_size_test, js_delivery_test,
        observable_test, players_test, request_mixin_test,
        translator_test, url_for_test, xhtml_normalization_test)
    from mediadrop.lib.services.tests import youtube_client_test
    from mediadrop.lib.storage.tests import youtube_storage_test
    from mediadrop.model.tests import (category_example_test, group_example_test, 
        media_example_test, media_status_test, media_test, user_example_test)
    from mediadrop.plugin.tests import abstract_class_registration_test, events_test, observes_test
    
    from mediadrop.validation.tests import (limit_feed_items_validator_test, 
        uri_validator_test)
    
    # do not export 'unittest' via '*' import from this module
    import unittest
    suite = unittest.TestSuite()
    for name, symbol in locals().items():
        if name.endswith('_test'):
            tests = getattr(symbol, 'suite')()
            suite.addTest(tests)
    return suite

if __name__ == '__main__':
    # do not export 'unittest' via '*' import from this module
    import unittest
    unittest.main(defaultTest='suite')
