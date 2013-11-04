# This file is a part of MediaDrop (http://www.mediadrop.net),
# Copyright 2009-2013 MediaDrop contributors
# For the exact contribution history, see the git revision log.
# The source code contained in this file is licensed under the GPLv3 or
# (at your option) any later version.
# See LICENSE.txt in the main project directory, for more information.

from mediadrop.lib.test.pythonic_testcase import *

from mediadrop.plugin.abc import (AbstractClass, AbstractMetaClass, 
    abstractmethod, ImplementationError)


class AbstractClassRegistrationTest(PythonicTestCase):
    class NameInterface(AbstractClass):
        @abstractmethod
        def name(self):
            pass
    
    class NameSizeInterface(NameInterface):
        @abstractmethod
        def size(self):
            pass
    
    class NameComponent(NameInterface):
        def name(self):
            return u'NameComponent'
    
    class NameSizeComponent(NameSizeInterface):
        def name(self):
            return u'NameSizeComponent'
        
        def size(self):
            return 42
    def tearDown(self):
        AbstractMetaClass._registry.clear()
    
    
    # --- tests ---------------------------------------------------------------
    
    def test_can_register_subclass(self):
        assert_length(0, list(self.NameInterface))
        
        self.NameInterface.register(self.NameComponent)
        assert_equals([self.NameComponent], list(self.NameInterface))
    
    def test_registration_checks_implementation_of_abstract_methods(self):
        class IncompleteImplementation(self.NameInterface):
            pass
        assert_raises(ImplementationError, 
                      lambda: self.NameInterface.register(IncompleteImplementation))
    
    def test_one_class_can_be_registered_for_multiple_base_classes_at_once(self):
        self.NameSizeInterface.register(self.NameSizeComponent)
        assert_equals([self.NameSizeComponent], list(self.NameInterface))
        assert_equals([self.NameSizeComponent], list(self.NameSizeInterface))
        
        self.NameInterface.register(self.NameComponent)
        assert_equals(set([self.NameComponent, self.NameSizeComponent]), 
                      set(self.NameInterface))


import unittest
def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(AbstractClassRegistrationTest))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='suite')
