# -*- coding: UTF-8 -*-
# Copyright 2014 Felix Schwarz
# The source code in this file is licensed under the MIT license.

from decorator import decorator


__all__ = ['dictify', 'listify', 'setify', 'tuplify']


def listify(func, iterable=list):
    def listify_wrapper(function, *args, **kwargs):
        results = []
        for result in function(*args, **kwargs):
            results.append(result)

        if isinstance(results, iterable):
            return results
        return iterable(results)
    return decorator(listify_wrapper, func)

def tuplify(func):
    return listify(func, iterable=tuple)

def setify(func):
    return listify(func, iterable=set)

def dictify(func):
    return listify(func, iterable=dict)
