################################################################################

from collections.abc import Mapping, Collection
import itertools

from . import _Derived

from .exceptions import *

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

class Map(_Derived, Mapping):

    def __init__(self, keys, values, /, **kwargs):
        super().__init__(tuple(keys), tuple(values), **kwargs)
        self._keys, self._values = self.terms

    def evaluate(self):
        return dict(unpack_gruples(*self._resolve_terms()))

    def _keyind(self, k):
        return tuple(self).index(k)
    def __iter__(self):
        return self._keys.__iter__()
    def __len__(self):
        return self._keys.__len__()

################################################################################
