################################################################################

from collections.abc import (
    Collection as _Collection,
    Iterable as _Iterable,
    Mapping as _Mapping,
    Hashable as _Hashable,
    )
from typing import Union as _Union, NoReturn as _NoReturn

from . import generic as _generic

class Gruple(_generic.FuncyIncisable, _Collection):
    __slots__ = ('_shape', '_flatlen', '_contents')
    def __init__(self, *args):
        self._contents = tuple(args)
        self._shape = (len(args),)
    @property
    def shape(self):
        return self._shape
    def _getitem_strict(self, ind: int, /) -> object:
        return self._contents[ind]
    def _getitem_broad(self,
            arg: _Union[slice, _Iterable, type(Ellipsis)], /
            ) -> object:
        if isinstance(arg, slice):
            return self._contents[arg]
        else:
            return tuple(self._contents[i] for i in arg)
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

class GrupleMap(Gruple, _Mapping):
    __slots__ = ('_asdict', '_keys', '_values')
    def __init__(self, pairs, /) -> None:
        self._asdict = dict(pairs)
        self._keys = tuple(self._asdict.keys())
        self._values = tuple(self._asdict.values())
        super().__init__(*self._keys)
    def _indconvert(self, ind: _Hashable, /, *, conAdd: int = 0) -> _Hashable:
        if ind in self._keys:
            ind = self._contents.index(ind) + conAdd
        return ind
    def _getitem_strict(self, ind: _Hashable, /) -> object:
        return self._values[self._indconvert(ind)]
    def _getitem_broad(self,
            ind: _Union[slice, _Iterable, type(Ellipsis)], /
            ) -> object:
        if ind is Ellipsis:
            return self._values
        elif isinstance(ind, slice):
            start = self._indconvert(ind.start)
            stop = self._indconvert(ind.stop, conAdd = 1)
            step = ind.step
            return self._values[start : stop : step]
        else:
            return tuple(self._getitem_strict(i) for i in ind)
    def __repr__(self):
        return 'Fn' + self._asdict.__repr__()

################################################################################