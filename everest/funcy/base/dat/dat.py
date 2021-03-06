################################################################################

from functools import cached_property as _cached_property
from typing import Union as _Union

from . import _Base, _generic

from .exceptions import *

class Dat(_Base):
    __slots__ = ('_shape', '_context')
    def __init__(self,
            *,
            shape: tuple = (),
            context: tuple = (),
            **kwargs,
            ) -> None:
        super().__init__(**kwargs)
        self._shape = shape
        self._context = context
    @property
    def shape(self):
        return self._shape
    def __getitem__(self, arg: _generic.FuncyIncisor, /) -> 'Dat':
        if self.atomic:
            raise IndexError("Cannot slice Dat of depth zero.")
        if (argType := type(arg)) is tuple:
            return self._get_tuple(*arg)
        elif isinstance(arg, _generic.FuncySlice):
            return self._get_slice(arg)
        else:
            return SubDat(self)
    def _get_tuple(self, *args) -> 'Dat':
        depth = self.depth
        if (nArgs := len(args)) > depth:
            raise IndexError(
                "Too many indices:"
                f" provided == {nArgs}; max allowed == {depth}."
                )
        raise NotYetImplemented
    def _get_slice(self, arg, /) -> 'Dat':
        raise NotYetImplemented
    @classmethod
    def _subdat_construct(cls):
        return SubDat

class SubDat(Dat):
    __slots__ = ('parent', 'argument')
    def __init__(self,
            parent: Dat,
            argument: _generic.FuncyIncisor
            /,
            *,
            context: tuple = (),
            **kwargs,
            ) -> None:
        self.parent = parent
        self.argument = argument
        super().__init__(
            shape = parent.shape[1:],
            context = tuple((*context, parent)),
            **kwargs,
            )
    def evaluate(self) -> object:
        return self.parent.value

class QuickDat(Dat):
    __slots__ = ('_value')
    def __init__(self, value, /, **kwargs) -> None:
        self._value = value
        super().__init__(**kwargs)
    def evaluate(self) -> object:
        return self._value

################################################################################