################################################################################

import itertools as _itertools
from collections.abc import Collection as _Collection, Iterable as _Iterable

from . import _generic, _GrupleMap, _unpacker_zip
from .group import Group as _Group, groups_resolve
from .derived import Derived as _Derived

from .exceptions import *

class Map(_Derived, _generic.FuncyMapping):

    def __init__(self, keys, values, /, **kwargs) -> None:
        keys, values = (self._group_convert(t) for t in (keys, values))
        super().__init__(keys, values, **kwargs)
        self._keys, self._values = self.terms

    @staticmethod
    def _group_convert(arg) -> _generic.FuncyContainer:
        if isinstance(arg, _generic.FuncyEvaluable):
            if isinstance(arg, _generic.FuncyContainer):
                return arg
        else:
            if isinstance(arg, _Collection):
                return _Group(*arg)
        raise TypeError(type(arg))

    def _evaluate(self, terms) -> object:
        return _GrupleMap(_unpacker_zip(*terms))

    @property
    def rawValue(self) -> _GrupleMap:
        assert not self.isSeq
        return _GrupleMap(
            _unpacker_zip(*(groups_resolve(t) for t in self.terms))
            )
    def _plainget(self, ind, /, asiter: bool = False) -> object:
        out = self.rawValue[self._value_resolve(ind)]
        return iter(out) if asiter else out
    def __setitem__(self,
            ind: _generic.FuncyShallowIncisor, val : object, /
            ) -> None:
        got = self._plainget(ind, asiter = True)
        for subgot, subval in _unpacker_zip(got, val):
            subgot.value = subval
    def __delitem__(self, ind: _generic.FuncyShallowIncisor, /) -> None:
        self[ind] = None

    def __iter__(self):
        return self._keys.__iter__()
    def __len__(self):
        return len(self.rawValue)

################################################################################
