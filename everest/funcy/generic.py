################################################################################

import numbers as _numbers
from array import ArrayType as _ArrayType
from functools import (
    cached_property as _cached_property,
    lru_cache as _lru_cache
    )

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



from .exceptions import *
class FuncyAbstractMethodException(FuncyException):
    ...


class FuncyNoneType(_ABC):
    ...
_ = FuncyNoneType.register(type(None))

class FuncySlice(_ABC):
    @_abstractmethod
    def indices(self, length: int, /) -> tuple:
        raise FuncyAbstractMethodException
    def iterable(self, length):
        return range(*self.indices(length))
_ = FuncySlice.register(slice)




class FuncyDatalike(_ABC):
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

class FuncyIterator(_ABC):
    ...
_ = FuncyIterator.register(_collabc.Iterator)

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

class FuncyMutableSequence(FuncySequence):
    ...
_ = FuncyMutableSequence.register(_collabc.MutableSequence)

class FuncyMapping(FuncyCollection):
    ...
_ = FuncyMapping.register(_collabc.Mapping)

class FuncyStruct(_ABC):
    @classmethod
    def __subclasshook__(cls, C):
        if cls is FuncyStruct:
            if all((
                    issubclass(C, FuncySequence),
                    not issubclass(C, FuncyMutableSequence)
                    )):
                return True
        return NotImplemented
# _ = FuncyStruct.register(tuple)



class FuncyIncisor(_ABC):
    ...
class FuncyStrictIncisor(FuncyIncisor):
    ...
_ = FuncyStrictIncisor.register(FuncyIntegral)
class FuncyDeepIncisor(FuncyIncisor):
    ...
_ = FuncyDeepIncisor.register(FuncyStruct)
class FuncyBroadIncisor(FuncyIncisor):
    ...
_ = FuncyBroadIncisor.register(FuncySlice)
_ = FuncyBroadIncisor.register(FuncySequence)

class FuncyIncisable(FuncyDatalike):
    @property
    @_abstractmethod
    def shape(self) -> tuple:
        raise FuncyAbstractMethodException
    @_cached_property
    def depth(self) -> int:
        return len(self.shape)
    @_cached_property
    def atomic(self) -> bool:
        return self.depth == 0
    @_abstractmethod
    def _getitem_strict(self, arg: FuncyStrictIncisor, /) -> FuncyDatalike:
        raise FuncyAbstractMethodException
    @_abstractmethod
    def _getitem_deep(self, arg: FuncyDeepIncisor, /) -> FuncyDatalike:
        raise FuncyAbstractMethodException        
    @_abstractmethod
    def _getitem_broad(self, arg: FuncyBroadIncisor, /) -> FuncyDatalike:
        raise FuncyAbstractMethodException
    @classmethod
    def _incision_methods(cls):
        yield from (
            (FuncyStrictIncisor, cls._getitem_strict),
            (FuncyDeepIncisor, cls._getitem_deep),
            (FuncyBroadIncisor, cls._getitem_broad),
            )
    @classmethod
    @_lru_cache
    def _get_incision_method(cls, argType: type, /):
        for typ, meth in cls._incision_methods():
            if issubclass(argType, typ):
                return meth
        return NotImplemented
    def __getitem__(self, arg: FuncyIncisor, /) -> FuncyDatalike:
        argType = type(arg)
        if not issubclass(argType, FuncyIncisor):
            raise TypeError(
                f"Incisor type {argType} is not a subclass of {FuncyIncisor}"
                )
        incisionMethod = self._get_incision_method(argType)
        if incisionMethod is NotImplemented:
            raise TypeError(f"FuncyIncisor type {argType} not accepted.")
        return incisionMethod(self, arg)

class FuncyArray(FuncyIncisable):
    def _get_redType(self):
        if (depth := self.depth) == 1:
            return self.dtype
        else:
            return self.__class__
_ = FuncyArray.register(_np.ndarray)

class FuncyEvaluable(_ABC):
    @_abstractmethod
    def evaluate(self) -> FuncyDatalike:
        raise FuncyAbstractMethodException
    @_cached_property
    def value(self) -> FuncyDatalike:
        return self.evaluate()

#     @_cached_property
#     def redType(self) -> FuncyDatalike:
#         redType = self._get_redType()
#         if not issubclass(redType, FuncyDatalike):
#             raise TypeError(f"Reduction type {redType} is not Datalike.")
#         if hasattr(redType, '_defaultdtype'):
#             if not issubclass(
#                     dtype := self.dtype,
#                     redTypeDtype := redType._defaultdtype,
#                     ):
#                 raise TypeError(
#                     f"Reduction dtype {redTypeDtype}"
#                     f"is not a superclass of parent dtype {dtype}"
#                     )
#         return redType
#     @_abstractmethod
#     def _get_redType(self):
#         raise FuncyAbstractMethodException

################################################################################
