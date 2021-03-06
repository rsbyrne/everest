################################################################################

import numbers as _numbers
from array import ArrayType as _ArrayType
from functools import cached_property as _cached_property

import numpy as _np




PRIMITIVETYPES = set((
    _numbers.Number,
    str,
    _np.ndarray,
    _ArrayType,
    type(None),
    tuple,
    ))



from abc import ABC as _ABC, abstractmethod as _abstractmethod



class FuncyNoneType(_ABC):
    ...
_ = FuncyNoneType.register(type(None))

class FuncySlice(_ABC):
    ...
_ = FuncySlice.register(slice)



class FuncyDatalike(_ABC):
    @classmethod
    def __subclasshook__(cls, C):
        if cls is FuncyDatalike:
            if any("_defaultdtype" in B.__dict__ for B in C.__mro__):
                return True
        return NotImplemented
    @classmethod
    def _check_dtype(cls, dtype) -> type:
        if type(dtype) is str:
            import numpy as np
            dtype = eval(dtype)
        if not type(dtype) is type:
            raise TypeError(
                "Provided dtype"
                " must be either a data type or a str evaluable as such."
                )
        if not issubclass(dtype, (default := cls._defaultdtype)):
            raise TypeError(
                f"Provided dtype {dtype} is not a subclass of {default}"
                )
        return dtype
    @_cached_property
    def dtype(self) -> type:
        try:
            return self._check_dtype(self._dtype)
        except AttributeError:
            return self._defaultdtype



class FuncyString(FuncyDatalike):
    _defaultdtype = str
_ = FuncyString.register(FuncyString._defaultdtype)

class FuncyBool(FuncyDatalike):
    _defaultdtype = bool
_ = FuncyBool.register(FuncyBool._defaultdtype)


class FuncyNumerical(FuncyDatalike):
    _defaultdtype = _numbers.Number

class FuncyNumber(FuncyNumerical):
    ...
_ = FuncyNumber.register(FuncyNumber._defaultdtype)

class FuncyComplex(FuncyNumber):
    _defaultdtype = _numbers.Complex
_ = FuncyComplex.register(FuncyComplex._defaultdtype)

class FuncyReal(FuncyComplex):
    _defaultdtype = _numbers.Real
_ = FuncyReal.register(FuncyReal._defaultdtype)

class FuncyRational(FuncyReal):
    _defaultdtype = _numbers.Rational
_ = FuncyRational.register(FuncyRational._defaultdtype)

class FuncyIntegral(FuncyRational):
    _defaultdtype = _numbers.Integral
_ = FuncyIntegral.register(FuncyIntegral._defaultdtype)



from collections import abc as _collabc

class FuncyContainer(_ABC):
    ...
_ = FuncyContainer.register(_collabc.Container)

class FuncyIterable(_ABC):
    ...
_ = FuncyIterable.register(_collabc.Iterable)

class FuncySized(_ABC):
    ...
_ = FuncySized.register(_collabc.Sized)

class FuncyCallable(_ABC):
    ...
_ = FuncyCallable.register(_collabc.Callable)

class FuncyCollection(FuncySized, FuncyIterable, FuncyContainer):
    ...
_ = FuncyCollection.register(_collabc.Collection)

class FuncyReversible(_ABC):
    ...
_ = FuncyReversible.register(_collabc.Reversible)

class FuncySequence(FuncyReversible, FuncyCollection):
    ...
_ = FuncySequence.register(_collabc.Sequence)

class FuncyMapping(FuncyCollection):
    ...
_ = FuncyMapping.register(_collabc.Mapping)



class FuncyIncisable(FuncyDatalike):
    @property
    @_abstractmethod
    def shape(self) -> tuple:
        return None
    @_cached_property
    def depth(self) -> int:
        return len(self.shape)
    @_cached_property
    def atomic(self) -> bool:
        return self.depth == 0
    @_abstractmethod
    def __getitem__(self, arg) -> FuncyDatalike:
        return None

class FuncyArray(FuncyIncisable):
    ...
_ = FuncyArray.register(_np.ndarray)

class FuncyIncisor(_ABC):
    ...
_ = FuncyIncisor.register(FuncySlice)
_ = FuncyIncisor.register(FuncyIntegral)

class FuncyEvaluable(_ABC):
    @_abstractmethod
    def evaluate(self) -> object:
        return None
    @_cached_property
    def value(self) -> object:
        return self.evaluate()

################################################################################
