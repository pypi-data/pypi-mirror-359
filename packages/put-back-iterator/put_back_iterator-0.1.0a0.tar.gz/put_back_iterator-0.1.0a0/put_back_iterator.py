from __future__ import absolute_import, division, print_function
import sys


_DEFAULT_PLACEHOLDER = object()

class PutBackIterator:
    def __init__(self, iterable):
        self._iterator = iter(iterable)
        self._put_back_stack = []

    def __iter__(self):
        return self

    def _next_impl(self, default=_DEFAULT_PLACEHOLDER):
        if self._put_back_stack:
            return self._put_back_stack.pop()
        else:
            end_sentinel = object()
            element_or_sentinel = next(self._iterator, end_sentinel)
            if element_or_sentinel is end_sentinel:
                if default is _DEFAULT_PLACEHOLDER:
                    raise StopIteration
                else:
                    return default
            else:
                return element_or_sentinel

    if sys.version_info < (3,):
        next = _next_impl
    else:
        __next__ = _next_impl

    def put_back(self, element):
        self._put_back_stack.append(element)

    def has_next(self):
        if self._put_back_stack:
            return True
        else:
            end_sentinel = object()
            element_or_sentinel = next(self, end_sentinel)
            if element_or_sentinel is end_sentinel:
                return False
            else:
                self._put_back_stack.append(element_or_sentinel)
                return True
