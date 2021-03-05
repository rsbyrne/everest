################################################################################

from collections.abc import Sequence as _Sequence
from typing import Optional as _Optional, Union as _Union

import numpy as _np

from . import _generic
from .numerical import (
    Numerical as _Numerical,
    NumericalConstructFailure,
    _check_dtype
    )

from .exceptions import *

class ArrayConstructFailure(NumericalConstructFailure):
    ...

class Array(_Numerical, _generic.FuncyArray):

    __slots__ = (
        'shape',
        '_memory',
        )
    def __init__(self, *, dtype, shape, initVal = _np.nan, **kwargs) -> None:
        initVal = _np.full(shape, initVal, dtype = dtype)
        super().__init__(
            dtype = dtype, shape = shape, initVal = initVal,
            **kwargs
            )
        self.shape = shape
        self._memory = self.memory

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

def construct_array(
        arg: _Optional[_Union[type, _Sequence, _np.ndarray]] = None,
        /, *args, **kwargs
        ) -> Array:
    if len(args):
        raise ArrayConstructFailure(
            "Cannot pass multiple args to array constructor"
            )
    kwargs = kwargs.copy()
    if not arg is None:
        if not isinstance(arg, _np.ndarray):
            try:
                arg = _np.array(arg)
            except Exception as e:
                raise ArrayConstructFailure(
                    f"Exception when converting arg to numpy array type: {e}"
                    )
        if not 'shape' in kwargs: kwargs['shape'] = arg.shape
        if not 'dtype' in kwargs: kwargs['dtype'] = arg.dtype
        if not 'initVal' in kwargs: kwargs['initVal'] = arg
    try:
        dtype = kwargs['dtype']
    except KeyError:
        raise ArrayConstructFailure(
            "No 'dtype' kwarg or arg interpretable as a datatype"
            " was provided to array constructor."
            )
    try:
        dtype = _check_dtype(dtype)
    except TypeError as e:
        raise ArrayConstructFailure(e)
    try:
        return Array(**kwargs)
    except Exception as e:
        raise ArrayConstructFailure(
            "Array construct failed"
            f" with args = {(arg, *args)}, kwargs = {kwargs};"
            f" {e}"
            )

################################################################################