################################################################################

from functools import cached_property as _cached_property
from numbers import (
    Real as _Real,
    Integral as _Integral
    )

from .variable import Variable as _Variable
from . import _special, _generic

from .exceptions import *

class NumericalConstructFailure(VariableConstructFailure):
    ...

class Numerical(_Variable, _generic.FuncyNumerical):

    __slots__ = (
        '_dtype',
        )

    def __init__(self, *, dtype = None, initVal = None, **kwargs):
        self._dtype = dtype
        super().__init__(dtype = self.dtype, initVal = initVal, **kwargs)

    @_cached_property
    def nullVal(self):
        if issubclass(self.dtype, _Integral):
            self.nullVal = _special.nullint
        else:
            self.nullVal = _special.nullflt

    def nullify(self):
        self.memory = self.nullVal
        self.refresh()
    @property
    def isnull(self):
        return isinstance(self.memory, _special.Null)

    def __iadd__(self, arg):
        self.memory += arg
        self.refresh()
        return self
    def __isub__(self, arg):
        self.memory -= arg
        self.refresh()
        return self
    def __imul__(self, arg):
        self.memory *= arg
        self.refresh()
        return self
    def __itruediv__(self, arg):
        self.memory /= arg
        self.refresh()
        return self
    def __ifloordiv__(self, arg):
        self.memory //= arg
        self.refresh()
        return self
    def __imod__(self, arg):
        self.memory %= arg
        self.refresh()
        return self
    def __ipow__(self, arg):
        self.memory **= arg
        self.refresh()
        return self

################################################################################
