################################################################################

from numbers import Rational as _Rational, Integral as _Integral
from typing import Optional as _Optional, Union as _Union

from . import _generic
from .numerical import (
    Numerical as _Numerical,
    NumericalConstructFailure,
    _check_dtype
    )

from .exceptions import *

class ScalarConstructFailure(NumericalConstructFailure):
    ...

class Scalar(_Numerical, _generic.FuncyNumber):

    __slots__ = (
        'shape',
        'memory',
        '_prev',
        'stack',
        '_rectified',
        )

    def __init__(self, *, initVal = None, **kwargs) -> None:
        super().__init__(initVal = initVal, **kwargs)
        self.shape = ()
        self._rectified = False

    def rectify(self):
        if not self._rectified:
            try:
                self.memory = self.dtype(self.memory)
                self._rectified = True
            except TypeError:
                if self.memory is Ellipsis:
                    self.memory = self._prev
                    self._rectified = True
                if self.isnull:
                    raise NullValueDetected
                elif hasattr(self.memory, '_funcy_setvariable__'):
                    self.memory._funcy_setvariable__(self)
                    self.rectify()
                else:
                    self.nullify()
                    raise TypeError(self.memory)

    def set_value(self, val):
        self._prev = self.memory
        self.memory = val
        self._rectified = False

class ScalarRational(Scalar, _generic.FuncyRational):
    def __init__(self, *, dtype = float, **kwargs) -> None:
        super().__init__(dtype = dtype, **kwargs)

class ScalarIntegral(Scalar, _generic.FuncyIntegral):
    def __init__(self, *, dtype = int, **kwargs) -> None:
        super().__init__(dtype = dtype, **kwargs)

def construct_scalar(
        arg: _Optional[_Union[type, _Rational]] = None,
        /, *args, **kwargs
        ) -> Scalar:
    if len(args):
        raise ScalarConstructFailure(
            "Cannot pass multiple args to scalar constructor"
            )
    kwargs = kwargs.copy()
    if not arg is None:
        if (argType := type(arg)) is type or argType is str:
            if 'dtype' in kwargs:
                raise ScalarConstructFailure(
                    "Cannot provide both arg-as-dtype and dtype kwarg"
                    " to scalar constructor"
                    )
            kwargs['dtype'] = arg
        else:
            if 'initVal' in kwargs:
                raise ScalarConstructFailure(
                    "Cannot provide both arg-as-initVal"
                    " and 'initVal' kwarg to scalar constructor."
                    )
            kwargs['initVal'] = arg
            if not 'dtype' in kwargs:
                kwargs['dtype'] = type(arg)
    try:
        dtype = kwargs['dtype']
    except KeyError:
        raise ScalarConstructFailure(
            "No 'dtype' kwarg or arg interpretable as a datatype"
            " was provided to scalar constructor."
            )
    try:
        dtype = _check_dtype(dtype)
    except TypeError as e:
        raise ScalarConstructFailure(e)
    if issubclass(dtype, _Rational):
        try:
            if issubclass(dtype, _Integral):
                return ScalarIntegral(**kwargs)
            else:
                return ScalarRational(**kwargs)
        except Exception as e:
            raise ScalarConstructFailure(
                "Scalar construct failed"
                f" with args = {(arg, *args)}, kwargs = {kwargs};"
                f" {e}"
                )
    else:
        raise ScalarConstructFailure(
            f"Provided dtype '{dtype}' not an acceptable type"
            " for scalar constructor."
            )

################################################################################