################################################################################

from collections.abc import (
    Collection as _Collection,
    Iterable as _Iterable,
    Mapping as _Mapping,
    Hashable as _Hashable,
    )
import operator as _operator
import itertools as _itertools
from typing import Union as _Union, NoReturn as _NoReturn

from . import generic as _generic
from .utilities import unpacker_zip as _unpacker_zip

class Gruple(_generic.FuncyIncisable, _Collection):
    __slots__ = ('_shape', '_flatlen', '_contents')
    def __init__(self, args: _Iterable, /):
        self._contents = tuple(args)
        self._shape = (len(self._contents),)
    @property
    def masklike(self):
        return all(isinstance(v, bool) for v in self)
    @property
    def shape(self):
        return self._shape
    def _getitem_strict(self, ind: int, /) -> object:
        return self._contents[ind]
    def _getitem_broad(self,
            ind: _Union[slice, _Iterable, type(Ellipsis)], /
            ) -> object:
        if ind is Ellipsis:
            vals = self._contents
        elif isinstance(ind, slice):
            vals = self._contents[ind]
        else:
            ind = Gruple(ind)
            if ind.masklike:
                ind = [i for i, v in enumerate(ind) if v]
            vals = (self._contents[i] for i in ind)
        return self.__class__(vals)
    def _getitem_deep(self, arg: tuple, /) -> _NoReturn:
        raise ValueError("Too many levels in provided index.")
    def __contains__(self, arg: object, /):
        return self._contents.__contains__(arg)
    def __iter__(self):
        return self._contents.__iter__()
    def __repr__(self):
        return 'Fn' + self._contents.__repr__()
    def copy(self):
        return self.__class__(*self._contents)
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

class GrupleMap(Gruple, _Mapping):
    __slots__ = ('_asdict', '_keys', '_values')
    def __init__(self, pairs, /) -> None:
        self._asdict = dict(pairs)
        self._keys = Gruple(self._asdict.keys())
        self._values = Gruple(self._asdict.values())
        super().__init__(self._keys)
    def _indconvert(self, ind: _Hashable, /, *, conAdd: int = 0) -> _Hashable:
        if ind in self._keys:
            ind = self._contents.index(ind) + conAdd
        return ind
    def _getitem_strict(self, ind: _Hashable, /) -> object:
        return self._values[self._indconvert(ind)]
    def _getitem_strict_pair(self, ind: _Hashable, /) -> object:
        ind = self._indconvert(ind)
        return self._keys[ind], self._values[ind]
    def _getitem_broad(self,
            ind: _Union[slice, _Iterable, type(Ellipsis)], /
            ) -> object:
        if ind is Ellipsis:
            vals, keys = self._values, self._keys
        elif isinstance(ind, slice):
            start = self._indconvert(ind.start)
            stop = self._indconvert(ind.stop, conAdd = 1)
            step = ind.step
            vals = self._values[start : stop : step]
            keys = self._keys[start : stop : step]
        else:
            ind = Gruple(ind)
            if ind.masklike:
                ind = [i for i, v in enumerate(ind) if v]
            vals, keys = zip((self._getitem_strict_pair(i)) for i in ind)
        return self.__class__(zip(keys, vals))
    def __repr__(self):
        return 'Fn' + self._asdict.__repr__()
    @classmethod
    def _rich(cls, self, other, /, *, opkey: str) -> 'GrupleMap':
        keys = self._keys
        if isinstance(other, _Mapping):
            keys = Gruple(k for k in keys if k in other)
            other = Gruple(other[k] for k in keys)
        vals = Gruple._rich(self._values, other, opkey = opkey)
        return cls(zip(keys, vals))

################################################################################
