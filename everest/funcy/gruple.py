################################################################################

from collections.abc import Sequence as _Sequence
from typing import Union as _Union, NoReturn as _NoReturn

from . import generic as _generic

class Gruple(_generic.FuncyUnpackable, _generic.FuncyIncisable):
    __slots__ = ('_shape')
    def __init__(self, *args):
        self.contents = tuple(args)
        self._shape = (len(args),)
    @property
    def shape(self):
        return self._shape
    def _getitem_strict(self, ind: int, /) -> object:
        return self.contents[ind]
    def _getitem_broad(self,
            arg: _Union[slice, _Sequence, type(Ellipsis)], /
            ) -> object:
        if isinstance(arg, slice):
            return self.contents[arg]
        else:
            return tuple(self.contents[i] for i in arg)
    def _getitem_deep(self, arg: tuple, /) -> _NoReturn:
        raise ValueError("Too many levels in provided index.")
    def __iter__(self):
        return iter(self.contents)
    def __repr__(self):
        return 'Fn' + repr(self.contents)
    def copy(self):
        return self.__class__(*self.contents)

################################################################################