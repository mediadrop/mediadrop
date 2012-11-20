# -*- coding: UTF-8 -*-
#
# The MIT License
# 
# Copyright (c) 2011-2012 Felix Schwarz <felix.schwarz@oss.schwarz.eu>
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
# I believe the license above is permissible enough so you can actually 
# use/relicense the code in any other project without license proliferation. 
# I'm happy to relicense this code if necessary for inclusion in other free 
# software projects.

# TODO / nice to have
#  - raising assertions (with message building) should be unified
#  - shorted tracebacks for cascaded calls so it's easier to look at the 
#    traceback as a user 
#      see jinja2/debug.py for some code that does such hacks:
#          https://github.com/mitsuhiko/jinja2/blob/master/jinja2/debug.py

from unittest import TestCase

__all__ = ['assert_almost_equals', 'assert_callable', 'assert_contains', 
           'assert_dict_contains', 'assert_equals', 'assert_false', 'assert_falseish',
           'assert_greater',
           'assert_isinstance', 'assert_is_empty', 'assert_is_not_empty', 
           'assert_length', 'assert_none', 
           'assert_not_contains', 'assert_not_none', 'assert_not_equals', 
           'assert_raises', 'assert_smaller', 'assert_true', 'assert_trueish', 
           'create_spy', 'PythonicTestCase', ]


def assert_raises(exception, callable, message=None):
    try:
        callable()
    except exception, e:
        return e
    default_message = u'%s not raised!' % exception.__name__
    if message is None:
        raise AssertionError(default_message)
    raise AssertionError(default_message + ' ' + message)

def assert_equals(expected, actual, message=None):
    if expected == actual:
        return
    default_message = '%s != %s' % (repr(expected), repr(actual))
    if message is None:
        raise AssertionError(default_message)
    raise AssertionError(default_message + ': ' + message)

def assert_none(actual, message=None):
    assert_equals(None, actual, message=message)

def assert_false(actual, message=None):
    assert_equals(False, actual, message=message)

def assert_falseish(actual, message=None):
    if not actual:
        return
    default_message = '%s is not falseish' % repr(actual)
    if message is None:
        raise AssertionError(default_message)
    raise AssertionError(default_message + ': ' + message)

def assert_true(actual, message=None):
    assert_equals(True, actual, message=message)

def assert_trueish(actual, message=None):
    if actual:
        return
    default_message = '%s is not trueish' % repr(actual)
    if message is None:
        raise AssertionError(default_message)
    raise AssertionError(default_message + ': ' + message)

def assert_length(expected_length, actual_iterable, message=None):
    assert_equals(expected_length, len(actual_iterable), message=message)

def assert_not_equals(expected, actual, message=None):
    if expected != actual:
        return
    default_message = '%s == %s' % (repr(expected), repr(actual))
    if message is None:
        raise AssertionError(default_message)
    raise AssertionError(default_message + ': ' + message)

def assert_almost_equals(expected, actual, max_delta=None, message=None):
    if expected == actual:
        return
    if (max_delta is not None) and (abs(expected - actual) <= max_delta):
        return
    
    if max_delta is None:
        default_message = '%s != %s' % (repr(expected), repr(actual))
    else:
        default_message = '%s != %s +/- %s' % (repr(expected), repr(actual), repr(max_delta))
    if message is None:
        raise AssertionError(default_message)
    raise AssertionError(default_message + ': ' + message)

def assert_not_none(actual, message=None):
    assert_not_equals(None, actual, message=message)

def assert_contains(expected_value, actual_iterable, message=None):
    if expected_value in actual_iterable:
        return
    default_message = '%s not in %s' % (repr(expected_value), repr(actual_iterable))
    if message is None:
        raise AssertionError(default_message)
    raise AssertionError(default_message + ': ' + message)

def assert_not_contains(expected_value, actual_iterable, message=None):
    if expected_value not in actual_iterable:
        return
    default_message = '%s in %s' % (repr(expected_value), repr(actual_iterable))
    if message is None:
        raise AssertionError(default_message)
    raise AssertionError(default_message + ': ' + message)

def assert_dict_contains(expected_sub_dict, actual_super_dict, message=None):
    for key, value in expected_sub_dict.items():
        assert_contains(key, actual_super_dict, message=message)
        if value != actual_super_dict[key]:
            failure_message = '%(key)s=%(expected)s != %(key)s=%(actual)s' % \
                dict(key=repr(key), expected=repr(value), actual=repr(actual_super_dict[key]))
            if message is not None:
                failure_message += ': ' + message
            raise AssertionError(failure_message)

def assert_is_empty(actual, message=None):
    if len(actual) == 0:
        return
    default_message = '%s is not empty' % (repr(actual))
    if message is None:
        raise AssertionError(default_message)
    raise AssertionError(default_message + ': ' + message)

def assert_is_not_empty(actual, message=None):
    if len(actual) > 0:
        return
    default_message = '%s is empty' % (repr(actual))
    if message is None:
        raise AssertionError(default_message)
    raise AssertionError(default_message + ': ' + message)

def assert_callable(value, message=None):
    if callable(value):
        return
    default_message = "%s is not callable" % repr(value)
    if message is None:
        raise AssertionError(default_message)
    raise AssertionError(default_message + ': ' + message)

def assert_isinstance(value, klass, message=None):
    if isinstance(value, klass):
        return

    def class_name(instance_or_klass):
        if isinstance(instance_or_klass, type):
            return instance_or_klass.__name__
        return instance_or_klass.__class__.__name__
    default_message = "%s (%s) is not an instance of %s" % (repr(value), class_name(value), class_name(klass))
    if message is None:
        raise AssertionError(default_message)
    raise AssertionError(default_message + ': ' + message)

def assert_smaller(smaller, greater, message=None):
    if smaller < greater:
        return
    default_message = '%s >= %s' % (repr(smaller), repr(greater))
    if message is None:
        raise AssertionError(default_message)
    raise AssertionError(default_message + ': ' + message)

def assert_greater(greater, smaller, message=None):
    if greater > smaller:
        return
    default_message = '%s <= %s' % (repr(greater), repr(smaller))
    if message is None:
        raise AssertionError(default_message)
    raise AssertionError(default_message + ': ' + message)

def create_spy(name=None):
    class Spy(object):
        def __init__(self, name=None):
            self.name = name
            self.reset()
        
        # pretend to be a python method / function
        @property
        def func_name(self):
            return self.name
        
        def __str__(self):
            if self.was_called:
                return "<Spy(%s) was called with args: %s kwargs: %s>" \
                    % (self.name, self.args, self.kwargs)
            else:
                return "<Spy(%s) was not called yet>" % self.name
        
        def reset(self):
            self.args = None
            self.kwargs = None
            self.was_called = False
            self.return_value = None
        
        def __call__(self, *args, **kwargs):
            self.args = args
            self.kwargs = kwargs
            self.was_called = True
            return self.return_value
        
        def and_return(self, value):
            self.return_value = value
            return self
        
        def assert_was_called_with(self, *args, **kwargs):
            assert_true(self.was_called, message=str(self))
            assert_equals(args, self.args, message=str(self))
            assert_equals(kwargs, self.kwargs, message=str(self))
        
        def assert_was_called(self):
            assert_true(self.was_called, message=str(self))
            
        def assert_was_not_called(self):
            assert_false(self.was_called, message=str(self))
    
    return Spy(name=name)


class PythonicTestCase(TestCase):
    def __getattr__(self, name):
        if name in globals():
            return globals()[name]
        return getattr(super(PythonicTestCase, self), name)

# is_callable

