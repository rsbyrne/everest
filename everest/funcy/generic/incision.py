################################################################################

from abc import ABC as _ABC, abstractmethod as _abstractmethod
from functools import (
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
            if all((
                    issubclass(C, FuncyIterable),
                    not issubclass(C, FuncyMapping),
                    not issubclass(C, (tuple, str, FuncyDatalike)),
                    )):
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
    def broadincision(self) -> type:
        return FuncyBroadIncision
    @property
    def subincision(self) -> type:
        return FuncySubIncision
    def _getitem_strict(self, arg, /):
        meti = self._get_meti(type(arg))
        for mets, v in self.items():
            if arg == mets[meti]:
                return v
        raise IndexError
    def _getitem_sub(self, *argn):
        return self.subincision(self, argn)
    def _getitem_trivial(self,
            arg: FuncyTrivialIncisor = None, /
            ) -> FuncyDatalike:
        return self
    def _getitem_deep(self, arg0, /, *argn) -> FuncyDatalike:
        if arg0 is None:
            return self._getitem_trivial()
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
        if isinstance(arg0, FuncyStrictIncisor):
            return cut[argn]
        else:
            return cut._getitem_sub(*argn)
    def _getitem_broad(self, arg: FuncyBroadIncisor, /):
        return self.broadincision(self, arg)
    def _getitem_shallow(self, arg: FuncyShallowIncisor, /):
        if isinstance(arg, FuncyBroadIncisor):
            return self._getitem_broad(arg)
        else:
            return self._getitem_strict(arg)
    def _incision_methods(self):
        yield from (
            (FuncyTrivialIncisor, self._getitem_trivial),
            (FuncyDeepIncisor, self._getitem_deep),
            (FuncyBroadIncisor, self._getitem_broad),
            (FuncyStrictIncisor, self._getitem_strict),
            )
    def _get_incision_method(self, arg, /):
        argType = type(arg)
        for typ, meth in self._incision_methods():
            if issubclass(argType, typ):
                return meth
        return NotImplemented
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
#         return incisionMethod
        if incisionMethod is NotImplemented:
            raise TypeError(
                f"FuncyIncisor type {type(toCheck)} not accepted."
                )
        return incisionMethod(*args)
    @property
    def depth(self) -> int:
        return len(self.shape)
    @property
    def atomic(self) -> bool:
        return self.depth == 0
    def __len__(self):
        if self.shape:
            return self.shape[0]
        else:
            return _special.nullint
    @property
    def metrics(self):
        return zip(*self._metrics())
    @property
    def metricTypes(self):
        return tuple(self._metricTypes())
    def _metrics(self):
        yield _itertools.repeat(True)
        yield _itertools.count()
    @classmethod
    def _metricTypes(cls):
        yield FuncyBool
        yield FuncyIntegral
    def _get_meti(self, argType, /):
        for i, metType in enumerate(self.metricTypes):
            if issubclass(argType, metType):
                return i
        raise TypeError(argType)
    def items(self):
        return zip(self.metrics, self)
    @_abstractmethod
    def __iter__(self):
        raise FuncyAbstractMethodException
    @property
    @_abstractmethod
    def shape(self) -> tuple:
        raise FuncyAbstractMethodException

class FuncyIncision(FuncyIncisable):
    __slots__ = '_source', '_incision',
    def __init__(self, source, incisor, /, *args, **kwargs):
        self._source, self._incisor = source, incisor
        super().__init__(*args, **kwargs)
    @property
    def source(self):
        return self._source
    @property
    def incisor(self):
        return self._incisor
    @property
    def shape(self):
        _, *dims = self.source.shape
        return tuple((_special.unkint, *dims))

class FuncyBroadIncision(FuncyIncision):
    __slots__ = '_iterFn',
    def _getitem_broad(self, arg: FuncyBroadIncisor, /):
        incisor = self.incisor[arg]
        return self.broadincision(self.source, incisor)
    def _iter_getslice(self):
        inc = self.incisor
        return _itertools.islice(self.source, inc.start, inc.stop, inc.step)
    def _iter_getinterval(self):
        inc = self.incisor
        start, stop, step = inc.start, inc.stop, inc.step
        start = 0 if start is None else start
        stop = _special.infint if stop is None else stop
        startmeti, stopmeti, stepmeti = (
            self._get_meti(type(s)) for s in (start, stop, step)
            )
        it = iter(self.source.items())
        started = False
        stopped = False
        try:
            while not started:
                mets, v = next(it)
                started = mets[startmeti] >= start
            if step is None:
                inner_loop = lambda _: next(it)
            else:
                def inner_loop(mets):
                    stepped = False
                    thresh = mets[stepmeti] + step
                    while not stepped:
                        mets, v = next(it)
                        stepped = mets[stepmeti] >= thresh
                    return mets, v
            while not stopped:
                yield v
                mets, v = inner_loop(mets)
                stopped = mets[stopmeti] >= stop
        except StopIteration:
            pass
    def _iter_getkeys(self):
        for i, (mets, v) in _seqmerge.muddle(
                (self.incisor, self.source.items())
                ):
            met = mets[self._get_meti(type(i))]
            if i == met:
                yield v
    def _iter_getmask(self):
        return (v for v, mask in zip(self.source, self.incisor) if mask)
    def __iter__(self):
        try:
            iterFn = self._iterFn
        except AttributeError:
            incisor = self.incisor
            if isinstance(incisor, FuncySlice):
                ss = incisor.start, incisor.stop, incisor.step
                if all(
                        isinstance(s, (FuncyNoneType, FuncyIntegral))
                            for s in ss
                        ):
                    iterFn = self._iter_getslice
                else:
                    iterFn = self._iter_getinterval
            elif isinstance(incisor, FuncyIterable):
                if all(isinstance(i, FuncyBool) for i in incisor):
                    iterFn = self._iter_getmask
                else:
                    iterFn = self._iter_getkeys
            else:
                raise TypeError(incisor, type(incisor))
            self._iterFn = iterFn
        return iterFn()

class FuncySubIncision(FuncyIncision):
    def __iter__(self):
        source, incisor = self.source, self.incisor
        for v in source:
            yield v[incisor]

class FuncyShallowIncisable(FuncyIncisable):
    @property
    def depth(self) -> int:
        assert len(self.shape) == 1
        return 1
    def _getitem_sub(self, arg, end = False):
        raise ValueError("Cannot slice that deep.")
    @property
    def subincision(self) -> type:
        return NotImplemented

################################################################################
