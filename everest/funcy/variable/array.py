################################################################################

from .exceptions import *

from functools import cached_property

import numpy as np

from .number import Number as _Number
from . import _special

class Array(_Number):

    __slots__ = (
        '_memory',
        )

    def __init__(self,
            arg1,
            arg2 = None,
            /,
            **kwargs
            ):
        if arg2 is None: # assume arg1 is or can be an array:
            if not isinstance(arg1, np.ndarray):
                arg1 = np.array(arg1)
            initVal = arg1
            dtype, shape = initVal.dtype.type, initVal.shape
            self._memory = initVal
        else:
            initVal = _special.null
            shape, dtype = arg1, arg2
            self._memory = np.empty(shape, dtype)
        super().__init__(
            shape = shape,
            dtype = dtype,
            _initVal = initVal,
            **kwargs
            )

    def set_value(self, val):
        try:
            self.memory[...] = val
        except NullValueDetected:
            self.memory = self._memory
            self.memory[...] = val

    def __setitem__(self, index, val):
        try:
            self.memory[index] = val
        except NullValueDetected:
            self.memory = self._memory
            self.memory[index] = val
        self.refresh()
    def __len__(self):
        return self.shape[0]

################################################################################
