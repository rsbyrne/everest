################################################################################

from abc import ABC as _ABC, abstractmethod as _abstractmethod
from functools import (
    cached_property as _cached_property,
    lru_cache as _lru_cache,
    reduce as _reduce
    )
import itertools as _itertools
import operator as _operator

from . import _special, _seqmerge
from .datalike import *

from .exceptions import *

class FuncyUnpackable(FuncyGeneric):
    @classmethod
    def __subclasshook__(cls, C):
        if cls is FuncyUnpackable:
            if issubclass(C, FuncyIterable) and not issubclass(C, FuncyMapping):
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
                    not issubclass(C, FuncyMapping),
                    not issubclass(C, FuncyString),
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





class FuncyIncisable(FuncySequence):
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
    def sibling(self) -> type:
        return FuncyBroadIncision
    @property
    def child(self) -> type:
        return self.sibling
    @property
    def subincision(self) -> type:
        return FuncySubIncision
    @_lru_cache
    def _getitem_strict(self, arg, /):
        for k, v in self.items():
            if k == arg:
                return v
        raise IndexError
#     @_abstractmethod
#     def _getitem_sub(self, arg0, /, *argn) -> 'FuncySubIncision':
#         raise FuncyAbstractMethodException
    def _getitem_sub(self, arg0, /, *argn):
        if len(argn):
            raise NotYetImplemented
        return self.subincision(source = self, incisor = arg)
    def _getitem_trivial(self, arg: FuncyTrivialIncisor, /) -> FuncyDatalike:
        return self
    def _getitem_deep(self, arg0, /, *argn) -> FuncyDatalike:
        if arg0 is None:
            return self._getitem_trivial(args)
        elif len(argn) + 1 > self.depth:
            raise ValueError("Cannot slice that deep.")
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
        return self.sibling(source = self, incisor = arg)
    def _getitem_shallow(self, arg: FuncyShallowIncisor, /):
        if isinstance(arg, FuncyBroadIncisor):
            return self._getitem_broad(arg)
        else:
            return self._getitem_strict(arg)
    @classmethod
    def _incision_methods(cls):
        yield from (
            (FuncyTrivialIncisor, cls._getitem_trivial),
            (FuncyDeepIncisor, cls._getitem_deep),
            (FuncyBroadIncisor, cls._getitem_broad),
            (FuncyStrictIncisor, cls._getitem_strict),
            )
    @classmethod
    @_lru_cache
    def _get_incision_method_from_type(cls, argType: type, /):
        for typ, meth in cls._incision_methods():
            if issubclass(argType, typ):
                return meth
        return NotImplemented
    @classmethod
    def _get_incision_method(cls, arg, /):
        return cls._get_incision_method_from_type(type(arg))
    def __getitem__(self, args: FuncyIncisor, /):
        if not type(args) is tuple:
            args = (args,)
        if len(args) == 1:
            toCheck = args[0]
        else:
            toCheck = args
        if not issubclass(type(toCheck), FuncyIncisor):
            raise TypeError(
                f"Incisor type {argType} is not a subclass of {FuncyIncisor}"
                )
        incisionMethod = self._get_incision_method(toCheck)
        if incisionMethod is NotImplemented:
            raise TypeError(f"FuncyIncisor type {type(toCheck)} not accepted.")
        return incisionMethod(self, *args)
    def __len__(self):
        if self.shape:
            return self.shape[0]
        else:
            return _special.nullint
    def items(self):
        return enumerate(self)
    @_abstractmethod
    def __iter__(self):
        raise FuncyAbstractMethodException

class FuncyIncision(FuncyIncisable):
    def __init__(self, *args, source, incisor, **kwargs):
        self._source, self._incisor = source, incisor
        super().__init__(*args, **kwargs)
    @property
    def shape(self):
        _, *dims = self.source.shape
        return tuple((_special.unkint, *dims))
    @property
    def incisor(self):
        return self._incisor
    @property
    def source(self):
        return self._source

class FuncyBroadIncision(FuncyIncision):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        incisor = self.incisor
        if isinstance(incisor, FuncySlice):
            self._iter = self._iter_getslice
        elif isinstance(incisor, FuncyIterable):
            self._iter = self._iter_getkeys
        else:
            raise TypeError(incisor, type(incisor))
    @property
    def sibling(self):
        return self.source.sibling
    @property
    def child(self):
        return self.source.child
    @property
    def subincision(self):
        return self.source.subincision
    def _getitem_broad(self, arg: FuncyBroadIncisor, /):
        incisor = self.incisor[arg]
        return self.sibling(source = self.source, incisor = incisor)
    def _iter_getslice(self):
        incisor = self.incisor
        return _itertools.islice(
            self.source,
            incisor.start, incisor.stop, incisor.step
            )
    def _iter_getkeys(self):
        for i, (ii, v) in _seqmerge.muddle(
                (self.incisor, self.source.items())
                ):
            if i == ii:
                yield v
    def __iter__(self):
        return self._iter()

class FuncySubIncision(FuncyIncision):
    @property
    def sibling(self):
        return self.source.child
    @property
    def child(self):
        return self.source.child
    @property
    def subincision(self):
        return self.source.subincision
    def __iter__(self):
        incisor = self.incisor
        for v in self.source:
            yield v[incisor]

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
