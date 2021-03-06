################################################################################

from functools import cached_property as _cached_property
from typing import Optional as _Optional

from . import _Base, _generic

from .exceptions import *

class Dat(_Base, _generic.FuncyIncisable):
    __slots__ = ('_shape', '_context')
    def __init__(self,
            *,
            shape: tuple = (),
            context: tuple = (),
            incisor: _Optional[_generic.FuncyIncisor, tuple] = None,
            **kwargs,
            ) -> None:
        self._shape = shape
        self._context = context
        self._incisor = incisor
        super().__init__(
            context = self.context,
            incisor = self.incisor,
            **kwargs
            )
    @property
    def shape(self):
        return self._shape
    @property
    def context(self):
        return self._context
    
#     def __getitem__(self, arg: _generic.FuncyIncisor, /) -> 'Dat':
#         if self.atomic:
#             raise IndexError("Cannot slice Dat of depth zero.")
#         if (argType := type(arg)) is tuple:
#             return self._get_tuple(*arg)
#         elif isinstance(arg, _generic.FuncySlice):
#             return self._get_slice(arg)
#         else:
#             return SubDat(self)
#     def _get_tuple(self, arg, /, *args) -> 'Dat':
#         depth = self.depth
#         if (nArgs := 1 + len(args)) > depth:
#             raise IndexError(
#                 "Too many indices:"
#                 f" provided == {nArgs}; max allowed == {depth}."
#                 )
#         raise NotYetImplemented
#     def _get_slice(self, arg, /) -> 'Dat':
#         raise NotYetImplemented
    @classmethod
    def _get_DatRed(self):
        return DatRed
    @_cached_property
    def DatRed(self):
        return self._get_DatRed()
    @classmethod
    def _get_DatOid(self)
        return DatOid
    @_cached_property
    def DatOid(self):
        return self._get_DatOid()
class DatOid(Dat):
    ...
class DatRed(Dat):
    __slots__ = ('parent', 'argument')
    def __init__(self,
            parent: Dat,
            incisor: _generic.FuncyIncisor,
            /,
            *,
            context: tuple = (),
            **kwargs,
            ) -> None:
        self.parent = parent
        super().__init__(
            shape = parent.shape[1:],
            context = tuple((*context, parent)),
            incisor = incisor,
            **kwargs,
            )
    def evaluate(self) -> _generic.FuncyDatalike:
        return self.parent.value[self.argument]

class QuickDat(Dat):
    __slots__ = ('_value')
    def __init__(self, value, /, **kwargs) -> None:
        self._value = value
        super().__init__(**kwargs)
    def evaluate(self) -> object:
        return self._value

################################################################################