################################################################################

import itertools as _itertools
from collections.abc import Collection as _Collection

from . import _generic, _Gruple, _unpacker_zip
from .group import Group as _Group
from .derived import Derived as _Derived

from .exceptions import *

class Map(_Derived, _generic.FuncyMapping):

    def __init__(self, keys, values, /, **kwargs):
        keys, values = (self._group_convert(t) for t in (keys, values))
        super().__init__(keys, values, **kwargs)
        self._keys, self._values = self.terms

    @staticmethod
    def _group_convert(arg):
        if isinstance(arg, _generic.FuncyEvaluable):
            if isinstance(arg, _generic.FuncyContainer):
                return arg
        else:
            if isinstance(arg, _Collection):
                return _Group(*arg)
        raise TypeError(type(arg))

    def evaluate(self):
        return dict(_unpacker_zip(*self._resolve_terms()))

    def _keyind(self, k):
        return tuple(self).index(k)
    def __iter__(self):
        return self._keys.__iter__()
    def __len__(self):
        return self._keys.__len__()

################################################################################
