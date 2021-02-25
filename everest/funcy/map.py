################################################################################
from .exceptions import *

from collections.abc import Mapping, Collection
import itertools

from .derived import Derived
from .base import Function
from .group import Group, Gruple
from .ops import ops

def unpack_gruples(ks, vs):
    for k, v in zip(ks, vs):
        if isinstance(k, Gruple):
            if isinstance(v, Gruple):
                if len(k) == len(v):
                    yield from unpack_gruples(k, v)
                else:
                    raise IndexError
            else:
                yield from unpack_gruples(k, itertools.repeat(v))
        elif isinstance(v, Gruple):
            yield from unpack_gruples(itertools.repeat(k), v)
        else:
            yield k, v

class Map(Derived, Mapping):
    def __init__(self, keys, values, /, **kwargs):
        keys, values = (self._proc_inp(o) for o in (keys, values))
        super().__init__(keys, values, **kwargs)
        self._keys, self._values = self.terms
    @staticmethod
    def _proc_inp(inp):
        if not isinstance(inp, Function):
            if isinstance(inp, Collection):
                inp = Group(*inp)
            else:
                inp = Group(inp)
        return inp
    def evaluate(self):
        return dict(unpack_gruples(*self._resolve_terms()))
    def __getitem__(self, key):
        return ops.getitem(self, key)
#         return self.value[self._value_resolve(key)]
    def _keyind(self, k):
        return tuple(self).index(k)
    def __iter__(self):
        return self._keys.__iter__()
    def __len__(self):
        return self._keys.__len__()
################################################################################
