################################################################################

from numbers import (
    Real as _Real,
    Integral as _Integral
    )

from .variable import Variable as _Variable
from . import _special, _generic

from .exceptions import *

class NumericalConstructFailure(VariableConstructFailure):
    ...

def _check_dtype(dtype) -> type:
    if type(dtype) is str:
        import numpy as np
        dtype = eval(dtype)
    if not type(dtype) is type:
        raise TypeError(
            "Provided dtype for scalar constructor"
            " must be either a data type or a str evaluable as such."
            )
    return dtype

class Numerical(_Variable, _generic.FuncyNumerical):

    __slots__ = (
        'dtype',
        'nullVal',
        )

    def __init__(self, *, dtype, initVal = None, **kwargs):
        dtype = _check_dtype(dtype)
        if issubclass(dtype, _Real):
            if issubclass(dtype, _Integral):
                self.nullVal = _special.nullint
            else:
                self.nullVal = _special.nullflt
        else:
            raise TypeError("Passed dtype must be a subclass of numbers.Real")
        self.dtype = dtype
        super().__init__(
            dtype = dtype, initVal = initVal,
            **kwargs
            )

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
