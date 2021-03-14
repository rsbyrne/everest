################################################################################

from abc import ABC as _ABC, abstractmethod as _abstractmethod
from functools import (
    cached_property as _cached_property,
    lru_cache as _lru_cache
    )

from . import _special
from .datalike import *

from .exceptions import *

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
    def __init__(self, *args, incisions = (), **kwargs):
        self._incisions = incisions
    @property
    def incisions(self):
        return self._incisions
    @property
    @_abstractmethod
    def shape(self) -> tuple:
        raise FuncyAbstractMethodException
    @property
    def depth(self) -> int:
        return len(self.shape)
    @property
    def atomic(self) -> bool:
        return self.depth == 0
    @property
    def sister(self) -> type:
        return self.__class__
    @property
    def daughter(self) -> type:
        return self.sister
    @_abstractmethod
    def _getitem_strict(self, arg: FuncyStrictIncisor, /) -> FuncyDatalike:
        raise FuncyAbstractMethodException
    @_abstractmethod
    def _getitem_sub(self, arg0 = Ellipsis, /, *argn):
        raise FuncyAbstractMethodException
    def _getitem_trivial(self, arg: FuncyTrivialIncisor, /) -> FuncyDatalike:
        return self
    def _getitem_deep(self, *args) -> FuncyDatalike:
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
        cut = self[arg0]
        if cut.depth < self.depth:
            return cut[argn]
        else:
            return cut._getitem_sub(*argn)
    def _getitem_broad(self, arg: FuncyBroadIncisor, /):
        return self.sister(incisions = (*self.incisions, arg))
    def _getitem_shallow(self, arg: FuncyShallowIncisor, /):
        if isinstance(arg, FuncyBroadIncisor):
            return self._getitem_broad(arg)
        else:
            return self._getitem_strict(arg)
    def _getitem_funcy(self, arg):
        return self[arg.value]
    @classmethod
    def _incision_methods(cls):
        yield from (
            (FuncyEvaluable, cls._getitem_funcy),
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
    def __getitem__(self, args: FuncyIncisor, /):
        if not type(args) is tuple:
            args = (args,)
        if len(args) == 1:
            argType = type(args[0])
        else:
            argType = type(args)
        if not issubclass(argType, FuncyIncisor):
            raise TypeError(
                f"Incisor type {argType} is not a subclass of {FuncyIncisor}"
                )
        incisionMethod = self._get_incision_method(argType)
        if incisionMethod is NotImplemented:
            raise TypeError(f"FuncyIncisor type {argType} not accepted.")
        return incisionMethod(self, *args)
    def __len__(self):
        if self.shape:
            return self.shape[0]
        else:
            return _special.nullint
    def __iter__(self):
        return (self[i] for i in range(len(self)))

class FuncyShallowIncisable(FuncyIncisable):
    @property
    def depth(self) -> int:
        assert len(self.shape) == 1
        return 1
    def _getitem_sub(self, arg, end = False):
        raise ValueError("Cannot slice that deep.")

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
