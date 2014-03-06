# -*- coding: UTF-8 -*-
# Copyright 2013 Felix Friedrich, Felix Schwarz
# The source code in this file is licensed under the MIT license.


__all__ = ['Result', 'ValidationResult']

class Result(object):
    def __init__(self, value, message=None):
        self.value = value
        self.message = message

    def __repr__(self):
        klassname = self.__class__.__name__
        return '%s(%r, message=%r)' % (klassname, self.value, self.message)

    def __eq__(self, other):
        if isinstance(other, self.value.__class__):
            return self.value == other
        elif hasattr(other, 'value'):
            return self.value == other.value
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __nonzero__(self):
        return self.value


class ValidationResult(Result):
    def __init__(self, value, validated_document=None, errors=None):
        self.value = value
        self.validated_document = validated_document
        self.errors = errors

    def __repr__(self):
        return 'ValidationResult(%r, validated_document=%r, errors=%r)' % (self.value, self.validated_document, self.errors)

