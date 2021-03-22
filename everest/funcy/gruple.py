################################################################################

from collections.abc import (
    Sequence as _Sequence,
    Iterable as _Iterable,
    Mapping as _Mapping,
    Hashable as _Hashable,
    )
import operator as _operator
import itertools as _itertools
from typing import Union as _Union, NoReturn as _NoReturn

from . import generic as _generic
from .utilities import unpacker_zip as _unpacker_zip

class _Gruple(_generic.FuncySoftIncisable, _Sequence):
    @property
    def incisionTypes(self):
        return {
            **super().incisionTypes,
            'broad': GrupleSwathe,
            }
    @property
    def flatlen(self):
        try:
            return self._flatlen
        except AttributeError:
            n = 0
            for c in self._contents:
                try:
                    n += c.flatlen
                except AttributeError:
                    if isinstance(c, _generic.FuncyUnpackable):
                        n += len(c)
                    else:
                        n += 1
            self._flatlen = n
            return n
    @classmethod
    def _rich(cls, self, other, /, *, opkey: str) -> 'Gruple':
        opfn = getattr(_operator, opkey)
        boolzip = (opfn(s, o) for s, o in _unpacker_zip(self, other))
        return cls(boolzip)
    def __lt__(self, other): return self._rich(self, other, opkey = 'lt')
    def __le__(self, other): return self._rich(self, other, opkey = 'le')
    def __eq__(self, other): return self._rich(self, other, opkey = 'eq')
    def __ne__(self, other): return self._rich(self, other, opkey = 'ne')
    def __gt__(self, other): return self._rich(self, other, opkey = 'gt')
    def __ge__(self, other): return self._rich(self, other, opkey = 'ge')

class Gruple(_Gruple):
    __slots__ = ('_flatlen', '_contents')
    def __init__(self, args: _Iterable, /):
        self._contents = tuple(args)
        super().__init__()
    def __iter__(self):
        yield from self._contents
    def copy(self):
        return self.__class__(*self._contents)
    @property
    def shape(self):
        return (len(self._contents),)
    def __repr__(self):
        return f'Gruple{list(self)}'
    def __str__(self):
        return self.__repr__()

class GrupleSwathe(_Gruple, _generic.FuncyBroadIncision):
    def __repr__(self):
        return f'Swath({repr(self.source)}[{repr(self.incisor)}])'
    def __str__(self):
        return str(list(self))

class _GrupleMap(_Gruple, _Mapping):
    @property
    def incisionTypes(self):
        return {
            **super().incisionTypes,
            'broad': GrupleMapSwathe,
            }
    def _metricTypes(self):
        yield from super()._metricTypes()
        yield object
    @classmethod
    def _rich(cls, self, other, /, *, opkey: str) -> 'GrupleMap':
        keys = self._keys
        if isinstance(other, _Mapping):
            keys = Gruple(k for k in keys if k in other)
            other = Gruple(other[k] for k in keys)
        vals = Gruple._rich(self._values, other, opkey = opkey)
        return cls(zip(keys, vals))

class GrupleMap(_GrupleMap):
    __slots__ = ('_asdict', '_keys', '_values')
    def __init__(self, pairs, /) -> None:
        self._asdict = dict(pairs)
        self._keys = Gruple(self._asdict.keys())
        self._values = Gruple(self._asdict.values())
        super().__init__()
    @property
    def shape(self):
        return (len(self._keys),)
    def _metrics(self):
        yield from super()._metrics()
        yield self._keys
    def __iter__(self):
        yield from self._values
    def __repr__(self):
        return f'GrupleMap{self._asdict}'

class GrupleMapSwathe(_GrupleMap, GrupleSwathe):
    ...

################################################################################
