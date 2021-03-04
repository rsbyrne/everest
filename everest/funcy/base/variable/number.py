################################################################################

from .variable import Variable as _Variable
from . import _special
from .exceptions import *

class Number(_Variable):

    __slots__ = (
        'shape',
        'dtype',
        )

    def __init__(self, shape = (), dtype = None, **kwargs):
        self.shape, self.dtype = shape, dtype
        super().__init__(shape = shape, dtype = dtype, **kwargs)

    def nullify(self):
        self.memory = _special.null
        self.refresh()
    @property
    def isnull(self):
        return self.memory is _special.null

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
