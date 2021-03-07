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
            **kwargs,
            ) -> None:
        self._shape = shape
        self._context = context
        super().__init__(
            context = self.context,
            **kwargs
            )
    @property
    def shape(self):
        return self._shape
    @property
    def context(self):
        return self._context

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