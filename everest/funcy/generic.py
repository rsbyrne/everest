################################################################################

from abc import ABC as _ABC, abstractmethod as _abstractmethod
import numbers as _numbers
from array import ArrayType as _ArrayType
from functools import (
    cached_property as _cached_property,
    lru_cache as _lru_cache
    )
import itertools as _itertools

import numpy as _np

from . import utilities as _utilities

from .exceptions import *
class FuncyAbstractMethodException(FuncyException):
    ...


PRIMITIVETYPES = set((
    int,
    float,
    complex,
    str,
    type(None),
    tuple,
    ))
class Primitive(_ABC):
    ...
for typ in PRIMITIVETYPES:
    _ = Primitive.register(typ)



class FuncyGeneric(_ABC):
    ...




class FuncyNoneType(FuncyGeneric):
    ...
_ = FuncyNoneType.register(type(None))

class FuncySlice(FuncyGeneric):
    @_abstractmethod
    def indices(self, length: int, /) -> tuple:
        raise FuncyAbstractMethodException
    def iterable(self, length):
        return range(*self.indices(length))
_ = FuncySlice.register(slice)



class FuncySeqlike(FuncyGeneric):
    ...



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



from collections import abc as _collabc

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


class FuncyUnpackable(FuncyGeneric):
    @classmethod
    def __subclasshook__(cls, C):
        if cls is FuncyUnpackable:
            if issubclass(C, FuncyIterable):
                if not issubclass(C, (tuple, str, FuncyDatalike)):
                    return True
        return NotImplemented

class FuncyStruct(FuncyGeneric):
    @classmethod
    def __subclasshook__(cls, C):
        if cls is FuncyStruct:
            if all((
                    issubclass(C, FuncyCollection),
                    not issubclass(C, FuncyMutableSequence),
                    not issubclass(C, FuncyUnpackable),
                    )):
                return True
        return NotImplemented
# _ = FuncyStruct.register(tuple)



class FuncyIncisor(FuncyGeneric):
    ...
class FuncyTrivialIncisor(FuncyIncisor):
    ...
_ = FuncyTrivialIncisor.register(type(Ellipsis))
_ = FuncyTrivialIncisor.register(type(None))
class FuncyShallowIncisor(FuncyIncisor):
    ...
class FuncyStrictIncisor(FuncyShallowIncisor):
    ...
_ = FuncyStrictIncisor.register(FuncyIntegral)
_ = FuncyStrictIncisor.register(FuncyString)
_ = FuncyStrictIncisor.register(FuncyMapping)
class FuncyBroadIncisor(FuncyShallowIncisor):
    ...
_ = FuncyBroadIncisor.register(FuncySlice)
_ = FuncyBroadIncisor.register(FuncyUnpackable)
class FuncyDeepIncisor(FuncyIncisor):
    ...
_ = FuncyDeepIncisor.register(FuncyStruct)


class FuncyIncisable(FuncyGeneric):
    @property
    @_abstractmethod
    def shape(self) -> tuple:
        raise FuncyAbstractMethodException
    def __len__(self):
        return self.shape[0]
    @_cached_property
    def depth(self) -> int:
        return len(self.shape)
    @_cached_property
    def atomic(self) -> bool:
        return self.depth == 0
    def _getitem_trivial(self, arg: FuncyTrivialIncisor, /) -> FuncyDatalike:
        return self
    @_abstractmethod
    def _getitem_strict(self, arg: FuncyStrictIncisor, /) -> FuncyDatalike:
        raise FuncyAbstractMethodException
    def _getitem_deep(self, args: FuncyDeepIncisor, /) -> FuncyDatalike:
        if not len(args):
            return self._getitem_trivial(args)
        elif len(args) > self.depth:
            raise ValueError("Cannot slice that deep.")
        arg0, *argn = args
        if arg0 is Ellipsis:
            if Ellipsis in argn:
                raise ValueError(
                    "Only one Ellipsis permitted for deep incision."
                    )
            arg0 = (slice(None) for _ in range(self.depth - len(argn)))
            arg0, *argn = (*arg0, *argn)
        argn = tuple(argn)
        if isinstance(arg0, FuncyBroadIncisor):
            out = self._getitem_broad(arg0)
            if len(argn):
                return out._getitem_sub(*argn)
            else:
                return out
        else:
            return self._getitem_strict(arg0)[argn]
    @_abstractmethod
    def _getitem_sub(self, arg0, /, *argn) -> FuncyDatalike:
        raise FuncyAbstractMethodException
    @_abstractmethod
    def _getitem_broad(self, arg: FuncyBroadIncisor, /) -> FuncyDatalike:
        raise FuncyAbstractMethodException
    def _getitem_shallow(self, arg: FuncyShallowIncisor, /) -> FuncyDatalike:
        if isinstance(arg, FuncyBroadIncisor):
            return self._getitem_broad(arg)
        else:
            return self._getitem_strict(arg)
    @classmethod
    def _incision_methods(cls):
        yield from (
            (FuncyTrivialIncisor, cls._getitem_trivial),
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

class FuncyShallowIncisable(FuncyIncisable):
    def _getitem_sub(self, arg, end = False):
        raise IndexError

class FuncyEvaluable(FuncyGeneric):
    @property
    @_abstractmethod
    def value(self) -> FuncyDatalike:
        raise FuncyAbstractMethodException

class FuncyVariable(FuncyEvaluable):
    @property
    @_abstractmethod
    def value(self) -> object:
        raise FuncyAbstractMethodException
    @value.setter
    @_abstractmethod
    def value(self, val, /) -> None:
        raise FuncyAbstractMethodException
    @value.deleter
    def value(self) -> None:
        self.value = None



#     def _get_redType(self):
#         if (depth := self.depth) == 1:
#             return self.dtype
#         else:
#             return self.__class__
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
