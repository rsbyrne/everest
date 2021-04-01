###############################################################################
''''''
###############################################################################

from abc import abstractmethod as _abstractmethod
import numbers as _numbers
from collections import abc as _collabc
from functools import cached_property as _cached_property

import numpy as _np

from .general import *

class FuncyDatalike(FuncyGeneric):
    _defaultdtype = object
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
        if isinstance(dtype, _np.dtype):
            dtype = _np.dtype.type
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
_ = FuncyBool.register(_np.bool_)

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

class FuncyArray(FuncyNumerical):
    ...
_ = FuncyArray.register(_np.ndarray)



class FuncyContainer(FuncyGeneric):
    ...
_ = FuncyContainer.register(_collabc.Container)

class FuncyIterable(FuncyGeneric):
    ...
_ = FuncyIterable.register(_collabc.Iterable)

class FuncyIterator(FuncyGeneric):
    ...
_ = FuncyIterator.register(_collabc.Iterator)

class FuncySized(FuncyGeneric):
    ...
_ = FuncySized.register(_collabc.Sized)

class FuncyCallable(FuncyGeneric):
    ...
_ = FuncyCallable.register(_collabc.Callable)

class FuncyCollection(FuncySized, FuncyIterable, FuncyContainer):
    ...
_ = FuncyCollection.register(_collabc.Collection)

class FuncyReversible(FuncyGeneric):
    ...
_ = FuncyReversible.register(_collabc.Reversible)

class FuncySequence(FuncyReversible, FuncyCollection):
    ...
_ = FuncySequence.register(_collabc.Sequence)

class FuncyMutableSequence(FuncySequence):
    ...
_ = FuncyMutableSequence.register(_collabc.MutableSequence)

class FuncyMapping(FuncyCollection):
    ...
_ = FuncyMapping.register(_collabc.Mapping)

class FuncyPotentiallySeqlike(FuncyGeneric):
    @property
    @_abstractmethod
    def isSeq(self) -> bool:
        raise FuncyAbstractMethodException
class FuncySeqlike(FuncyPotentiallySeqlike, FuncyIterable):
    @property
    def isSeq(self):
        return True

###############################################################################
''''''
###############################################################################
